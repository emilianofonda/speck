cardAI = DeviceProxy("d09-1-c00/ca/sai.1")
cardAI.user_readconfig=[\
cardAI.get_attribute_config(["averagechannel0"])[0],\
cardAI.get_attribute_config(["averagechannel1"])[0],\
cardAI.get_attribute_config(["averagechannel2"])[0],\
cardAI.get_attribute_config(["averagechannel3"])[0]]

ct.slaves2arm.append(cardAI)

ct.reinit()
