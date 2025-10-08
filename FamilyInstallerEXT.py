from TDStoreTools import StorageManager
import TDFunctions as TDF
from FamilyUtils import FamilyUtils
from installer import GenericInstallerEXT
import platform
import json 
import os
import tdu


class FamilyInstallerEXT(FamilyUtils):
    """
    FamilyInstallerEXT description 
    """
    def __init__(self, ownerComp): 
        # The component to which this extension is attached
        self.ownerComp = ownerComp



        family_name = self.ownerComp.par.Family.eval()
        color = self.ownerComp.parGroup.Color.eval() 
        # Create the generic installer with custom family name
        # You can customize the color - this example uses a blue shade
        self.installer = GenericInstallerEXT(
            ownerComp=ownerComp,
            family_name=family_name,
            color=color,  # Blue-ish color, adjust as needed
            compatible_types=["DAT"]
        )
    


    def Install(self):
        """
        Your custom installation logic can go here, 
        called after the generic installer completes
        """
        if self.ownerComp.par.Install:
            self.installer.Install()
           
            
            # First, verify the custom_operators folder exists
            custom_ops_folder = self.ownerComp.op('custom_operators')
            if not custom_ops_folder:
                # print(f"ERROR: 'custom_operators' folder not found in {self.ownerComp.path}")
                return
            
            # Check if there are any operators in the folder
            master_ops = custom_ops_folder.findChildren(depth=1)
            # print(f"Found {len(master_ops)} master operators in custom_operators folder")
            
            for custom_op in master_ops:
                if not custom_op.isCOMP and not custom_op.isBase:
                    # print(f"Skipping {custom_op.path} - not a COMP/Base") # Adjusted check
                    continue
                
                # print(f"Processing master operator: {custom_op.path} with tags {custom_op.tags}")
                
                # Add the base family tag if not already present
                if self.ownerComp.par.Family.eval() not in custom_op.tags:
                    custom_op.tags.add(self.ownerComp.par.Family.eval())
                
                # Add specific type tags based on the master operator name
                master_name = custom_op.name  # The name of the master operator
                
                # Add the specific type tag that follows the pattern {type}{family}
                type_tag = f"{master_name}{self.ownerComp.par.Family.eval()}"
                custom_op.tags.add(type_tag)
                # print(f"Added type tag '{type_tag}' to {custom_op.path}")
                
                # Handle FamilyUtils copying
                target_util = custom_op.op('FamilyUtils')
                if target_util:
                    target_util.text = self.ownerComp.op('FamilyUtils').text
                    target_util.expose = False
                else:
                    # Copy the FamilyUtils into the custom_op if it doesn't exist
                    custom_op.copy(self.ownerComp.op('FamilyUtils'))
                    new_util = custom_op.op('FamilyUtils')
                    new_util.expose = False
                    
                # Find and tag all DATs that start with 'out'
                try:
                    # First let's see ALL the DATs in each operator
                    all_dats = custom_op.findChildren(type=DAT, depth=1)
                    if all_dats:
                        # print(f"Found {len(all_dats)} total DATs:")
                        for dat in all_dats:
                            # print(f"  - {dat.name}")
                            if dat.name.startswith('out') or dat.name.startswith('output'):
                                # print(f"    This is an output DAT! Current tags: {dat.tags}")
                               pass
                    else:
                        # print("No DATs found at all")
                        pass
                except Exception as e:
                    if hasattr(op,'Logger'):
                        op.Logger.Error(me,f"Error processing DATs in {custom_op.name}: {e}")
                    else:
                        print(f"Error processing DATs in {custom_op.name}: {e}")
            
            if hasattr(op,'Logger'):
                op.Logger.Info(me,self.ownerComp.par.Family.eval() + " specific installation complete")
            else:
                print(self.ownerComp.par.Family.eval() + " specific installation complete")

        else:
            self.installer.Uninstall()
            if hasattr(op,'Logger'):
                op.Logger.Info(me,self.ownerComp.par.Family.eval() + " specific uninstallation complete")
            else:
                print(self.ownerComp.par.Family.eval() + " specific uninstallation complete")

    def PlaceOp(self, panelValue, name):
             
        return True

    def PostPlaceOp(self, clone):
       
        
        return

    def selfDestroy(self):
        """
        Clean up both the generic installer and this component
        """
        self.installer.selfDestroy()
        self.ownerComp.destroy()
        return

    def Showbuiltin(self):  
        self.ownerComp.showCustomOnly = 1- self.ownerComp.par.Showbuiltin.eval()

    def Updateall(self):
        """
        Updates all components of this family type to the newest version.
        """
        self.installer.Updateall()

    def Createstubs(self):
        """
        Creates lightweight stubs for all operators of this family.

        """
        self.installer.Createstubs()

    def Replacestubs(self):
        """
        Regenerates full components from stubs.
        """
        self.installer.Replacestubs()

