from json import loads, dumps
from os import path, mkdir, listdir
from typing import Optional, Tuple, List
from models import UserInformations

def check_database():

    if (not path.isdir(r"./data")):

        mkdir(path=r"./data")
        for i in ["users", "settings"]:

            if (not path.isdir(fr"./data/{i}")):
        
                mkdir(fr"./data/{i}")
    
    if (not path.isfile(r"./data/settings/channels.json")):

        with open(r"./data/settings/channels.json", "a+") as file:

            file.write(
                dumps(
                    {
                        "channels_id": []
                    },
                    indent=4
                )
            )

            file.close()
        
check_database()



class UserDatabase:

    def __init__(self, user_id: int) -> None:

        self.user_id = user_id
        self.path = r"./data/users"

    @property
    def there_is_user(self) -> bool:

        if (f"{self.user_id}.json" in listdir(self.path)):

            return True
        
        return False

    @property
    def user_informations(self) -> UserInformations:
        
        if (self.there_is_user):

            with (open(f"{self.path}/{self.user_id}.json", "r") as file):

                data = UserInformations(**loads(file.read()))
                file.close()

            return data

        add = self.add_user()
        if (add): self.user_informations

    @staticmethod
    def best_member(num: int) -> List[Tuple[int, int]]:

        all_files, files = listdir(r"./data/users"), []
        for file in all_files:

            if (str(file.split(".")[0]).isnumeric() and str(file.endswith(".json"))): files.append(file)
        
        best_users = []
        for file in files:

            try:

                with open(fr"./data/users/{str(file).split('.')[0]}.json", "r") as user:

                    data = loads(user.read())

                    if ("referral" in list(data.keys())): 

                        best_users.append(
                            (
                                len(data["referral"]),
                                int(data["user_id"])
                            )
                        )
                    del data
                    user.close()

            except:

                pass
        
        best_users.sort(key=lambda num: num[0])
        best_users.reverse()
        del (all_files, files)
        return best_users[:num]

    def add_user(self,phone_number: str, referraler: int | None = None) -> bool:

        if (not self.there_is_user):

            with (open(fr"{self.path}/{self.user_id}.json", "a+") as file):
                
                data = dumps(
                    {
                        "user_id": int(self.user_id),
                        "phone_number": str(phone_number),
                        "balance": 0,
                        "referral": []
                    },
                    indent=4
                )

                file.write(data)
                file.close()
            
            if (str(referraler).isnumeric() and
                UserDatabase(int(referraler)).there_is_user
            ):

                with (open(fr"{self.path}/{referraler}.json", "r")) as file:

                    data = loads(file.read())
                    file.close()

                if (not int(self.user_id) in data["referral"]):

                    with (open(fr"{self.path}/{referraler}.json", "w")) as file_write:

                        data["referral"].append(int(self.user_id))
                        data = dumps(data, indent=4)
                        file_write.write(data)
                        file_write.close()
                    

        return True

    def edit_balance(self, amount: int, sub_or_sum: Optional[str] = "sum") -> bool:

        if (not str(amount).isnumeric()): raise ValueError("amount must be a number")
        if (not sub_or_sum.lower() in ["sum", "sub"]): raise ValueError("sub_or_sum must in ['sum', 'sub']")

        if (self.there_is_user):

            with (open(f"{self.path}/{self.user_id}.json", "r") as file):

                data = loads(file.read())
                if (sub_or_sum.lower() == "sum"): data["balance"] += int(amount)
                else: data["balance"] -= int(amount)
                data = dumps(
                    data,
                    indent=4
                )
                
            with (open(f"{self.path}/{self.user_id}.json", "w") as file):

                file.write(data)
                file.close()
            
            return True
        
        self.add_user()
        self.edit_balance(amount, sub_or_sum)


        if (self.there_is_user):

            pass
    
              
class ChannelDatabase:


    def __init__(self, channel_id: int) -> None:

        self.channel_id = channel_id
        self.path = r"./data/settings/channels.json"

    @property
    def there_is_channel(self) -> bool:

        with (open(self.path, "r") as file):

            data: dict = loads(file.read())
            file.close()

            if (int(self.channel_id) in data["channels_id"]):return True
            else: return False
    
    @staticmethod
    def get_channels() -> list:

        with (open(fr"./data/settings/channels.json", "r") as file):

            data = loads(file.read())
            file.close()
            return data["channels_id"]

    def channel_edit(self, add_or_remove: str) -> bool:

        if (add_or_remove.lower() not in ["add", "remove"]): raise ValueError("add_or_remove must be add or remove")

        if ((not self.there_is_channel and add_or_remove == "add") or
            (self.there_is_channel and add_or_remove == "remove")):

            with (open(self.path, "r") as file):

                data = loads(file.read())
                try: data["channels_id"].append(int(self.channel_id)) if (add_or_remove.lower() == "add") else data["channels_id"].remove(int(self.channel_id))
                except: pass
                data = dumps(
                    data,
                    indent=4
                )
                file.close()

            with (open(self.path, "w") as file):

                file.write(data)
                file.close()

        return True
    

class Database:

    user = UserDatabase
    channel = ChannelDatabase

