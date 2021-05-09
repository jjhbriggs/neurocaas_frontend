import sys
import os
import json

path = "/home/ubuntu/ncap/neurocaas/ncap_iac/user_profiles"
os.chdir(path)
stacks = os.listdir()
for stack in stacks:
    new_path = path + "/" + stack
    if os.path.isdir(new_path):
        os.chdir(new_path)
        try:
            with open(new_path + "/user_config_template.json") as f:
                try:
                    data_array = json.load(f)
                    pipelines = data_array['UXData']["Affiliates"][0]["Pipelines"]
                    if not str(sys.argv[1]) in pipelines:
                        pipelines.append(str(sys.argv[1]))
                        data_array['UXData']["Affiliates"][0]["Pipelines"] = pipelines
                        with open(new_path + "/user_config_template.json", 'w') as outfile:
                            json.dump(data_array, outfile)
                    print("Succeeded on stack: " + stack)
                except:
                    print("Failed on stack: " + stack)
        except:
            print("ignored folder: " + new_path)