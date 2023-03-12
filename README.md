# cai-blender-rigtools
Rigging tools for blender based on [The Art of Effective Rigging](https://pieriko.artstation.com/store/57e1/the-art-of-effective-rigging-in-blender) course by [Pierrick Picaut](https://www.artstation.com/pieriko).

This addon helps automatize certain steps which had to be done manually during the rigging worklow.

**Note**: Due to its convoluted nature, for automated rigging it is advised to use Rigify or other tools instead of this. There may be a a Rigify feature set plugin made for this in the future. **This is an experimental addon, use at your own risk.**


## Installation
- Download the repository
- Copy `cai_rigtools` folder into Blender `scripts/addons/` directory
- Enable addon `Caiwan Rig Tools` Blender in settings

## Usage 
Once the addon is enabled a sub-menu `Rig Tools` should be added in **edit mode** under **Armature** menu and **pose mode** under **Pose** menu.

### Edit mode 

#### Create Target rig
Creates a copy of the selected deformation rig then applies copy constraints to it. The reason for that is this second rig can be manipulated freely with any complex mechanism but the original deforming rig can be completely detached. This helps exporting the rig later.

1. Select the bones to be copied
2. `Armature -> Rig Tools -> Create Target Rig` 
3. The newly created bones are remain selected 

Then these bones can be moved freely ot another layer.

#### Create bone lever rig

#### Create tail rig

#### Create tentacle rig

### Pose mode 

#### Clear all constraints
Clears of all assigned constraints from the selected bones

## Development 
TBD
