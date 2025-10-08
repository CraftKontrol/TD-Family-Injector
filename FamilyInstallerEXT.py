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

        # Create a Dependency to track venv path
        self.LOPvenv = tdu.Dependency("") 

        family_name = self.ownerComp.par.Family.eval()
        color = self.ownerComp.parGroup.Color.eval() 
        # Create the generic installer with CHATTD family name
        # You can customize the color - this example uses a blue shade
        self.installer = GenericInstallerEXT(
            ownerComp=ownerComp,
            family_name=family_name,
            color=color,  # Blue-ish color, adjust as needed
            compatible_types=["DAT"]
        )
        self.ownerComp.par.Lopsheader.label = ''

        self._initialize_venv_path()


    def _get_target_chattd(self):
        """Gets the ChatTD component expected inside this installer component."""
        # target_chattd_op_path = self.ownerComp.par.Chattdcomp.eval() # Removed parameter read
        target_chattd = self.ownerComp.op('ChatTD') # Find ChatTD directly inside
        if not target_chattd:
            #print("LOPs Install: ChatTD component not found inside installer.")
            return None
        if 'ChatTD' not in target_chattd.tags:
             #print(f"LOPs Install: Found op 'ChatTD' but it is missing the 'ChatTD' tag.")
             return None
        return target_chattd


    def _get_chattd_install_path(self):
        """Get ChatTD installation path from system AppData/Support dir config.json"""
        system = platform.system()
        if system == 'Windows':
            base_dir = os.path.join(os.getenv('APPDATA'), 'ChatTD')
        elif system == 'Darwin':  # macOS
            base_dir = os.path.expanduser('~/Library/Application Support/ChatTD')
        else:
            if hasattr(op,'Logger'):
                op.Logger.Error(me,"LOPs Install: Unsupported OS for getting install path config.")
            else:
                print("LOPs Install: Unsupported OS for getting install path config.")
            return None
                
        os.makedirs(base_dir, exist_ok=True)
        config_file = os.path.join(base_dir, 'config.json')
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f).get('python_venv')
            except Exception as e:
                if hasattr(op,'Logger'):
                    op.Logger.Error(me,f"LOPs Install: Error reading config file {config_file}: {e}")
                else:
                    print(f"LOPs Install: Error reading config file {config_file}: {e}")
                return None

        return None

    def _set_chattd_install_path(self, venv_path):
        """Save ChatTD installation path to system AppData/Support dir config.json"""
        system = platform.system()
        if system == 'Windows':
            base_dir = os.path.join(os.getenv('APPDATA'), 'ChatTD')
        elif system == 'Darwin':  # macOS
            base_dir = os.path.expanduser('~/Library/Application Support/ChatTD')
        else:
            if hasattr(op,'Logger'):
                op.Logger.Error(me,"Unsupported OS for setting install path config.")
            else:
                print("LOPs Install: Unsupported OS for setting install path config.")
            return False
                
        os.makedirs(base_dir, exist_ok=True)
        config_file = os.path.join(base_dir, 'config.json')
        try:
            with open(config_file, 'w') as f:
                json.dump({'python_venv': venv_path}, f)
            # print(f"LOPs Install: Updated config file {config_file} with path: {venv_path}")
            return True
        except Exception as e:
            if hasattr(op,'Logger'):
                op.Logger.Error(me,f"Error writing config file {config_file}: {e}")
            else:
                print(f"LOPs Install: Error writing config file {config_file}: {e}")
            return False


    def _initialize_venv_path(self):
        """Prioritizes local config, then parameter, to set ChatTD Venv path."""
        target_chattd = self._get_target_chattd()
        if not target_chattd:
            self.LOPvenv.val = ""
            return

        local_config_path = self._get_chattd_install_path()
        current_param_path = target_chattd.par.Pythonvenv.eval()
        final_path_to_set = None

        # 1. Check local config file path first
        if local_config_path and os.path.isdir(local_config_path):
            # print(f"LOPs Install: Found valid path in local config: {local_config_path}")
            final_path_to_set = local_config_path
        # 2. If local config invalid/missing, check current parameter value
        elif current_param_path and os.path.isdir(current_param_path):
            # print(f"LOPs Install: Using valid path from parameter: {current_param_path}")
            final_path_to_set = current_param_path
            self._set_chattd_install_path(final_path_to_set)
        else:
            # print("LOPs Install: No valid Venv path found in local config or parameter.")
            if target_chattd.par.Pythonvenv.eval() != '':
                 target_chattd.par.Pythonvenv = ''
                #  print("LOPs Install: Cleared ChatTD Pythonvenv parameter.")
            self.LOPvenv.val = ""
            return
        
        if target_chattd.par.Pythonvenv.eval() != final_path_to_set:
            target_chattd.par.Pythonvenv = final_path_to_set
            if hasattr(op,'Logger'):
                op.Logger.Info(me,f"Set ChatTD Pythonvenv parameter to: {final_path_to_set}")
            else:   
                print(f"LOPs Install: Set ChatTD Pythonvenv parameter to: {final_path_to_set}")
        
        # Update the installer's Basefolder parameter to match
        if self.ownerComp.par.Basefolder.eval() != final_path_to_set:
            self.ownerComp.par.Basefolder = final_path_to_set
            if hasattr(op,'Logger'):
                op.Logger.Info(me,f"Set Installer Basefolder parameter to: {final_path_to_set}")
            else:
                print(f"LOPs Install: Set Installer Basefolder parameter to: {final_path_to_set}")

        self._set_chattd_install_path(final_path_to_set)
        
        # Update the environment path in dependency
        self._update_env_path(final_path_to_set)

    def _update_env_path(self, path):
        """Update the venv path in the dependency if it's valid."""
        if not path or not os.path.isdir(path):
            self.LOPvenv.val = ""
            return
            
        # Basic check: look for typical venv folders
        if os.path.isdir(os.path.join(path, 'Lib')) or \
           os.path.isdir(os.path.join(path, 'lib')) or \
           os.path.isdir(os.path.join(path, 'bin')) or \
           os.path.isdir(os.path.join(path, 'Scripts')):
            # It's a valid venv path, store it
            self.LOPvenv.val = path
        else:
            # Not a valid venv, clear the path
            self.LOPvenv.val = ""

    def Install(self):
        """
        Your custom installation logic can go here, 
        called after the generic installer completes
        """
        if self.ownerComp.par.Install:
            self.installer.Install()
            #self.Checkinstall()
            
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
                                if 'LOP' not in dat.tags:
                                    dat.tags.add('LOP')
                                    # print(f"Added LOP tag. New tags: {dat.tags}")
                    else:
                        # print("No DATs found at all")
                        pass
                except Exception as e:
                    if hasattr(op,'Logger'):
                        op.Logger.Error(me,f"Error processing DATs in {custom_op.name}: {e}")
                    else:
                        print(f"Error processing DATs in {custom_op.name}: {e}")
            
            # print("CHATTD specific installation complete")
        else:
            self.installer.Uninstall()
            # print("CHATTD specific uninstallation complete")

    def PlaceOp(self, panelValue, name):
        chattd_op = self._get_target_chattd()
        if not chattd_op:
             #print("Cannot place OP, ChatTD component not found.")
             return True # Allow default placement maybe?

        if panelValue == 1:
            chattd_op.openParameters()
            return False
        if panelValue == 2:
            python_manager_op = chattd_op.op('python_manager')
            if python_manager_op: python_manager_op.openParameters()
            return False        
        return True

    def PostPlaceOp(self, clone):
        chattd_op = self._get_target_chattd()
        if not chattd_op:
            return

        if hasattr(clone.par, 'Model'):
            clone.par.Apiserver.val = chattd_op.par.Apiserver.val    
            clone.par.Model.val = chattd_op.par.Model.val
            
        if clone.name.startswith('dat_') or clone.name.startswith('comp_'):
            try:
                if clone.name.startswith('comp_'):
                    new_name = clone.name.replace('comp_', '')
                else:
                    new_name = clone.name.replace('dat_', '')
                clone.name = new_name
            except Exception as e:
                base_name = new_name.rstrip('0123456789')
                existing_ops = [op.name for op in clone.parent().findChildren(name=base_name+'*')]
                counter = 1
                while f"{base_name}{counter}" in existing_ops:
                    counter += 1
                unique_name = f"{base_name}{counter}"
                clone.name = unique_name
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

    def Basefolder(self):
        """
        Sets the ChatTD Python Venv path and updates the local config.
        """
        target_chattd = self._get_target_chattd()
        if not target_chattd:
            return
        
        new_path = self.ownerComp.par.Basefolder.eval()
        if new_path and os.path.isdir(new_path):
            target_chattd.par.Pythonvenv = new_path
            self._set_chattd_install_path(new_path)
            self._update_env_path(new_path)  # Update the dependency
        else:
            if hasattr(op,'Logger'):
                op.Logger.Error(me,f"Invalid path specified in Basefolder: {new_path}")
            else:   
                print(f"LOPs Install: Invalid path specified in Basefolder: {new_path}")
            self.LOPvenv.val = ""  # Clear the dependency if path is invalid
        return new_path
        
    def Installlops(self):
        """
        Triggers the full LOPs installation process, including:
        - Folder selection dialog
        - Python venv creation
        - Dependency installation
        This will use ChatTD's existing installer function.
        """
        target_chattd = self._get_target_chattd()
        if not target_chattd:
            if hasattr(op,'Logger'):
                op.Logger.Error(me,"Cannot install - ChatTD component not found")
            else:
                print("LOPs Install: Cannot install - ChatTD component not found")
            return
            
        # Check if ChatTD has the Installlops method - new approach:
        # Since Installlops is an exposed method, we can call it directly
        try:
            if hasattr(op,'Logger'):
                op.Logger.Info(me,"Triggering LOPs installation process...")
            else:
                print("LOPs Install: Triggering LOPs installation process...")
            # Call ChatTD's installation method directly since it's exposed
            target_chattd.Installlops()
            
            # After installation completes, refresh the Basefolder parameter with the new path
            new_path = target_chattd.par.Pythonvenv.eval()
            if new_path and os.path.isdir(new_path):
                self.ownerComp.par.Basefolder = new_path
                if hasattr(op,'Logger'):
                    op.Logger.Info(me,f"Installation completed. Path set to: {new_path}")
                else:
                    print(f"LOPs Install: Installation completed. Path set to: {new_path}")
        except AttributeError:
            if hasattr(op,'Logger'):
                op.Logger.Error(me,"ChatTD does not have the Installlops method")
            else:
                print("LOPs Install: ChatTD does not have the Installlops method")
            
    def Checkinstall(self):
        """
        Checks the installation status, prioritizing local config, and initializes paths.
        - Ensures all paths are synchronized between local config and parameters
        - Reports installation status
        - Sets appropriate paths 
        
        Use this to verify/fix installation issues or when opening on a new machine.
        """
        # print("LOPs Install: Checking installation...")
        target_chattd = self._get_target_chattd()
        if not target_chattd:
            if hasattr(op,'Logger'):
                op.Logger.Error(me,"Cannot check installation - ChatTD component not found")
            else:
                print("LOPs Install: Cannot check installation - ChatTD component not found")
            self.LOPvenv.val = ""
            return False
            
        # Check local config
        local_config_path = self._get_chattd_install_path()
        
        # Check if local config path exists and is valid
        if local_config_path and os.path.isdir(local_config_path):
            if hasattr(op,'Logger'):
                op.Logger.Info(me,f"LOPs Install: Found valid installation at: {local_config_path}")
            else:
                print(f"LOPs Install: Found valid installation at: {local_config_path}")

            # Set both parameters to ensure consistency
            target_chattd.par.Pythonvenv = local_config_path
            self.ownerComp.par.Basefolder = local_config_path
            
            # Verify python_manager's setup
            python_manager_op = target_chattd.op('python_manager')
            if python_manager_op:
                # print("LOPs Install: Triggering python_manager path setup...")
                python_manager_op.Addtosyspath()
            
            # Update env path
            self._update_env_path(local_config_path)
            return True
        else:
            # Check parameter value as fallback
            param_path = target_chattd.par.Pythonvenv.eval()
            if param_path and os.path.isdir(param_path):
                if hasattr(op,'Logger'):
                    op.Logger.Info(me,f"LOPs Install: Using path from parameter: {param_path}")
                else:
                    print(f"LOPs Install: Using path from parameter: {param_path}")
                self._set_chattd_install_path(param_path)  # Update config
                self.ownerComp.par.Basefolder = param_path # Ensure consistency
                self._update_env_path(param_path)
                return True
            else:
                if hasattr(op,'Logger'):
                    op.Logger.Error(me,"LOPs Install: No valid installation found.")
                else:
                    print("LOPs Install: No valid installation found.")
                self.LOPvenv.val = ""
                return False

