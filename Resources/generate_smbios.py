from Data import smbios_data, os_data

def set_smbios_model_spoof(model):
    try:
        smbios_data.smbios_dictionary[model]["Screen Size"]
        # Found mobile SMBIOS
        if model.startswith("MacBookAir"):
            if smbios_data.smbios_dictionary[model]["Screen Size"] == 13:
                return "MacBookAir7,2"
            elif smbios_data.smbios_dictionary[model]["Screen Size"] == 11:
                return "MacBookAir7,1"
            else:
                # Unknown Model
                raise Exception
        elif model.startswith("MacBookPro"):
            if smbios_data.smbios_dictionary[model]["Screen Size"] == 13:
                return "MacBookPro12,1"
            elif smbios_data.smbios_dictionary[model]["Screen Size"] >= 15:
                # 15" and 17"
                try:
                    smbios_data.smbios_dictionary[model]["Switchable GPUs"]
                    return "MacBookPro11,5"
                except KeyError:
                    return "MacBookPro11,4"
            else:
                # Unknown Model
                raise Exception
        elif model.startswith("MacBook"):
            if smbios_data.smbios_dictionary[model]["Screen Size"] == 13:
                return "MacBookAir7,2"
            elif smbios_data.smbios_dictionary[model]["Screen Size"] == 12:
                return "MacBook9,1"
            else:
                # Unknown Model
                raise Exception
        else:
            # Unknown Model
            raise Exception
    except KeyError:
        # Found desktop model
        if model.startswith("MacPro") or model.startswith("Xserve"):
            return "MacPro7,1"
        elif model.startswith("Macmini"):
            return "Macmini7,1"
        elif model.startswith("iMac"):
            if smbios_data.smbios_dictionary[model]["Max OS Supported"] <= os_data.os_data.high_sierra:
                # Models dropped in Mojave either do not have an iGPU, or should have them disabled
                return "iMacPro1,1"
            else:
                return "iMac17,1"
        else:
            # Unknown Model
            raise Exception