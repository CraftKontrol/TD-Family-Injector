# This look on the custom_operators folder for all the components inside the names network.
# All ops must be inside the Operator network. Sections are created for each Sub Network Inside.
# It take the names of each sections and make a table for all of that.

# me - this DAT
# scriptOp - the OP which is cooking
#
# press 'Setup Parameters' in the OP to call this function to re-create the parameters.
def onSetupParameters(scriptOp):
	page = scriptOp.appendCustomPage('Custom')
	p = page.appendFloat('Valuea', label='Value A')
	p = page.appendFloat('Valueb', label='Value B')
	return

# called whenever custom pulse parameter is pushed
def onPulse(par):
	return

def onCook(scriptOp):
	scriptOp.clear()

	CustomOps = op('custom_operators')
	
	# Look for all the components inside the Operators network.
	Categories = []
	Operators = []

	for node in CustomOps.op('generators').enclosedOPs:
		#print(node.name, node.type)
		if node.type != 'annotate':
			Operators.append(node)
		else:
			Categories.append(node)

	struct = []
	# For each category, look for enclosed operators
	for cat in Categories:
		newStruct = [cat, []]
		for node in cat.enclosedOPs:
			#print(cat.name + " / " + node.name)
			newStruct[1].append(node)
		struct.append(newStruct)

	header = []
	for Categories, ops in struct:
		# Add a column for each category in struct
		header.append(Categories.par.Titletext.eval())
	scriptOp.appendRow(header)

	maxRows = 0
	for Categories, ops in struct:
		if len(ops) > maxRows:
			maxRows = len(ops)	

	# Add rows for each operator in each category
	for i in range(maxRows):
		newRow = []
		for Categories, ops in struct:
			if i < len(ops):
				newRow.append(ops[i].name)
			else:
				newRow.append('')
		scriptOp.appendRow(newRow)



	return
