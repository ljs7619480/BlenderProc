import yaml
import numpy as np

class BrackList(list):
    pass

def represent_brack_list(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)
yaml.add_representer(BrackList, represent_brack_list)


class ConfigBuilder():
    def __init__(self, global_outpath, write_cam_state=True, write_light_state=True, blender_install_path="/home/<env:USER>/blender/"):
        self.output_path = global_outpath
        self.write_cam_state = write_cam_state
        self.write_light_state = write_light_state
        self.blender_install_path = blender_install_path
        self.config = dict()
        self.reset()

    def reset(self):
        self.config.clear()
        self.config["version"] = 3
        self.config["setup"] = {
            "blender_install_path": self.blender_install_path
        }
        self.config["modules"] = [{
            "module": "main.Initializer",
            "config":{
                "global": {
                    "output_dir": self.output_path
                }
            }
        }]

    def cameraLoader(self, poses, intrinsic_mat, resolution):
        """
            
            poses: list of [loc_x, loc_y, loc_z, rot_euler_x, rot_euler_y, rot_euler_z]
            intrinsic:  (3x3) intrinsic_mat
            resolution: (1x2) [resolurion_x, resolution_y]
        """
        module = {
            "module": "camera.CameraLoader",
            "config": {
                "cam_poses": [{
                    "location": BrackList(pose[:3]),
                    "rotation": {
                        "value": BrackList(pose[3:])
                    }  
                } for pose in poses],
                "default_cam_param": {
                    "cam_K": BrackList(intrinsic_mat.flatten().tolist()),
                    "resolution_x": resolution[0],
                    "resolution_y": resolution[1]
                }
            }
        }
        self.config["modules"].append(module)

    def lightLoader(self, poses, energy):
        """
            poses: list of [loc_x, loc_y, loc_z, rot_euler_x, rot_euler_y, rot_euler_z]
        """
        module = {
            "module": "lighting.LightLoader",
            "config": {
                "lights": [{
                    "type": "POINT",
                    "location": BrackList(pose[:3]),
                    "rotation": BrackList(pose[3:]),
                    "energy": energy
                } for pose in poses]
            }
        }
        self.config["modules"].append(module)

    def plyLoader(self, path):
        module = {
            "module": "loader.ReplicaLoader",
            "config": {
                "data_path" : path,
                "data_set_name": "",
            }
        }
        self.config["modules"].append(module)
        
        module = {
            "module": "manipulators.MaterialManipulator",
            "config": {
                "selector": {
                    "provider": "getter.Material",
                    "conditions": {"name": "ReplicaMaterial"}
                },
                "cf_change_to_vertex_color": "Col"
            }
        }
        self.config["modules"].append(module)

    def rgbRender(self, samples, color_key="colors", depth_key="depths"):
        module = {
            "module": "renderer.RgbRenderer",
            "config": {
                "samples": samples,
                "output_key": color_key,
                "render_distance": (depth_key is not None),
                "distance_output_key": depth_key
            }
        }
        self.config["modules"].append(module)

    def setWriter(self):
        if self.write_light_state:
            module = {
                "module": "writer.LightStateWriter",
                "config": {
                    "attributes_to_write": ["location", "rotation_euler", "energy"]
                }
            }
            self.config["modules"].append(module)
        if self.write_cam_state:
            module = {
                "module": "writer.CameraStateWriter",
                "config": {
                    "attributes_to_write": ["location", "rotation_euler"]
                }
            }
            self.config["modules"].append(module)
        module = {
            "module": "writer.Hdf5Writer",
            "config": {
                "postprocessing_modules": {
                    "distance": [{"module": "postprocessing.TrimRedundantChannels"}]
                }
            }
        }
        self.config["modules"].append(module)

    def dump(self, path):
        self.setWriter()
        res = yaml.dump(self.config,sort_keys=False)
        with open(path, 'w') as f:
            f.write(res)
        return res

if __name__ == "__main__":
    builder = ConfigBuilder("/tmp/foo/")
    builder.plyLoader("/home/ljs/workspace/BlenderProc/examples/vertexCol/")
    builder.lightLoader([[5, -5, 5, 0, 0, 0]], 1000)
    builder.cameraLoader(
        poses=[(0, 0, 0.5, 0, 0, 0), 
               (0.353, 0, 0.353, 0, 0.785, 0),
               (0.5, 0, 0, 0, 1.57, 0)],
        intrinsic_mat=np.array(
            [[616.95214844, 0.          , 324.23962402],
             [0.          , 617.11254883, 239.48379517],
             [0.          , 0.          , 1.          ]]),
        resolution=[640,480]
    )
    builder.rgbRender(350)
    print(builder.dump('/tmp/foo.yml'))