# me - this DAT
# panelValue - the PanelValue object that changed
# prev - the previous value of the PanelValue object that changed
# Make sure the corresponding toggle is enabled in the Panel Execute DAT.
import ctypes

def onOffToOn(panelValue):
	return

def whileOn(panelValue):
	return

def onOnToOff(panelValue):
	return

def whileOff(panelValue):
	return

def onValueChange(panelValue, prev):
    if(op('current')[0,0].val != "OPNAME"): return
    license = op.OPNAME.op('License')
    if(panelValue == -1): return
    
    op_fam = op.OPNAME.op('OP_fam')
    rows_per_column = parent.OPCREATE.op('nodetable').par.tablerows.eval()

    # Get the valid operator count for this group
    group_starts = []
    group_operators = []
    current_group = -1
    operator_count = 0
    
    for i in range(op_fam.numRows):
        if op_fam[i, 'type'].val.endswith('defLabel'):
            if current_group >= 0:
                group_operators.append(operator_count)
            group_starts.append(i)
            current_group += 1
            operator_count = 0
        elif op_fam[i, 'name'].val:
            operator_count += 1
    
    group_operators.append(operator_count)
    # Calculate total columns needed for each group
    columns_per_group = []
    for ops in group_operators:
        # If ops is exactly rows_per_column, we still need 2 columns because of header
        if ops == rows_per_column:
            cols = 2
        else:
            cols = (ops + (rows_per_column - 1)) // rows_per_column
        columns_per_group.append(cols)

    # Handle both regular clicks and ENTER key
    target_index = -1
    if panelValue == -9999:  # ENTER key
        destil = parent.OPCREATE.op('nodetable/destil')
        if destil.numRows > 1:
            selected_name = destil[1,0].val
            # Find the selected name in op_fam
            for i in range(op_fam.numRows):
                if op_fam[i, 'name'].val == selected_name:
                    target_index = i
                    break
    else:
        # Original click logic
        column_number = panelValue // rows_per_column
        
        # Find which group this column belongs to
        columns_counted = 0
        actual_group_index = 0
        for i, cols in enumerate(columns_per_group):
            if column_number < columns_counted + cols:
                actual_group_index = i
                break
            columns_counted += cols
        # Calculate position within the found group
        columns_into_group = column_number - columns_counted
        if columns_into_group == 0:  # First column of group
            position_in_group = (panelValue % rows_per_column) - 1  # Subtract 1 for header
        else:  # Overflow column
            operators_in_previous_columns = rows_per_column - 1
            position_in_group = operators_in_previous_columns + (panelValue % rows_per_column)
        # Validate position is within group's operator count
        if position_in_group >= group_operators[actual_group_index]:
            return
        # Get the actual operator
        group_start = group_starts[actual_group_index]
        target_index = group_start + 1 + position_in_group
    # Common validation for both click and ENTER
    if target_index == -1 or target_index >= op_fam.numRows:
        return

    if not op_fam[target_index, 'name'].val:
        return
    display_name = op_fam[target_index, 'name'].val
    lookup_name = display_name
    normalized_name = lookup_name.replace(' ', '_')
    

    # # Manage Config case
    # if lookup_name == 'ggen':
    #     op.GGen.openParameters()
    #     parent.OPCREATE.par.winclose.pulse()
    #     return


    # # Manage UI case
    # if lookup_name == 'ui':
    #     op.GGen.op('custom_operators').op('ui').par.winopen.pulse()
    #     parent.OPCREATE.par.winclose.pulse()
    #     return

    # # Manage common networks cases
    # if lookup_name == 'splatmaps':
    #      #check if globalshortcut exists
    #      if hasattr(op, 'SplatmapsNetwork'):
    #         # open floating network
    #         p = ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name="GGen Splatmap Network")
    #         p.owner = op.SplatmapsNetwork.op('UserNetwork')
    #         parent.OPCREATE.par.winclose.pulse()
    #         return    
    # if lookup_name == 'terrain':
    #     if hasattr(op, 'TerrainNetwork'):
    #         # open floating network
    #         p = ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name="GGen Terrain Network")
    #         p.owner = op.TerrainNetwork.op('UserNetwork')
    #         parent.OPCREATE.par.winclose.pulse()
    #         return

    if hasattr(op.OPNAME, 'PlaceOp'):
        if not op.OPNAME.PlaceOp(panelValue, lookup_name):
            parent.OPCREATE.par.winclose.pulse()
            return
    #print(lookup_name)
    master = op.OPNAME.op('custom_operators').findChildren(name=lookup_name, maxDepth=1)[0]
    clone = op.OPNAME.copy(master, name=normalized_name+'1')
    clone.allowCooking = True
    clone.bypass = False
   

    clone.viewer = ui.preferences['network.viewer']
    ui.panes.current.placeOPs([clone], inputIndex=0, outputIndex=0)
    parent.OPCREATE.par.winclose.pulse()
    if hasattr(op.OPNAME, 'PostPlaceOp'):
        op.OPNAME.PostPlaceOp(clone)