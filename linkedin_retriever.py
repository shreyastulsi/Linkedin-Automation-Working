from linkedin_api import Linkedin
import os
from dotenv import load_dotenv
import json
import concurrent
import pandas as pd
load_dotenv()

class LinkedInRetrieverError(Exception):
    pass


class LinkedInRetriever():
    def __init__(self, customEmail: str | None = None, customPassword: str | None = None) -> None:
        email, psw = os.getenv("LINKEDIN_EMAIL"), os.getenv("LINKEDIN_PSW")

        if customEmail and customPassword:
            email = customEmail
            psw = customPassword

        if not email or not psw:
            raise LinkedInRetrieverError("No LinkedIn authentication variables")

        self.KEY_FEATURES = ["firstName", "lastName", "summary", "geoLocationName", "countryName", "experience", "education", "publications", "certifications", "volunteer", "honors", "projects", "skills", "headline"]
        self.IGNORE_KEYWORDS = ["Urn", "logo", "expires", "picture", "https", "courses", "trackingId", "backgroundImage", "publicIdentifier", "url", "region", "img", "id", "elt", "backfilled", "universalName"]
 
        self.VALIDATION_FEATURES = ["firstName", "lastName", "geoLocationName", "experience", "education", "skills", "headline"]

        try:
            self.api = Linkedin(email, psw)
        except:
            raise LinkedInRetrieverError("Invalid LinkedIn authentication supplied.")

    def retrieve(self, profile: str) -> dict:
        if ("https" in profile or "linkedin.com" in profile) and "/" in profile:
            if profile[-1] == "/":
                profile = profile[:-1]

            profile = profile.split("/")[-1]

        try:
            profileData = self.api.get_profile(profile)
            print(f"Retrieved data for {profile}")

            return profileData
        
        except KeyError:
            raise LinkedInRetrieverError(f"Invalid linkedin profile name '{profile}' passed in")

    def print_keys(self, data: dict, originPath: str = None):
        for key, val in data.items():
            newPath = f"{originPath} -> {key}" if originPath else key
            
            if isinstance(val, dict):
                self.print_keys(val, originPath=newPath)
            else:
                print(newPath) 
    
    def filter_ignore_keys(self, key: str) -> bool:
        for i in self.IGNORE_KEYWORDS:
            if i.lower() in key.lower():
                return True
        return False

    def clean_data(self, preprocessed) -> dict | None:
        if isinstance(preprocessed, dict):
            result = {}
            for key, value in preprocessed.items():
                if self.filter_ignore_keys(key):
                    if isinstance(value, dict):
                        rooted = {}
                        for subkey, subvalue in value.items():
                            if subkey in self.KEY_FEATURES:
                                rooted[subkey] = self.clean_data(subvalue)
                        result.update(rooted)
                else:
                    cleaned_value = self.clean_data(value)
                    if cleaned_value is not None:
                        result[key] = cleaned_value
            return result
        
        elif isinstance(preprocessed, list):
            return [self.clean_data(item) for item in preprocessed if item is not None]
        
        else:
            if isinstance(preprocessed, str) and self.filter_ignore_keys(preprocessed):
                return None
            return preprocessed
        
    def save(self, processedDataset: dict, writeFolder: str, writeFile: str, erase: bool):
        returnPath = os.getcwd()

        os.makedirs(writeFolder, exist_ok=True)
        os.chdir(writeFolder)

        if ".txt" not in writeFile:
            writeFile += ".txt"

        created = True if not os.path.exists(writeFile) else False
        
        print(created)

        try:
            serialized = json.dumps(processedDataset)
        except:
            raise LinkedInRetrieverError("Serialization failed. Invalid map object")

        if erase:
            with open(writeFile, "w") as f:
                f.write(serialized)
                f.close()
                print(f"SAVED to {writeFile}")

                os.chdir(returnPath)
                return
        else:
            currentData = None
            if not created:
                with open(writeFile, "r") as f:
                    currentData = f.read()
                    f.close()

            try:
                final = []
                if currentData:
                    deserialized = json.loads(currentData)
                    final.append(deserialized)

                final.append(processedDataset)

                writeData = json.dumps(final)

                with open(writeFile, "w") as f:
                    f.write(writeData)
                    f.close()

                    print(f"SAVED to {writeFile}")
                    
                    os.chdir(returnPath)
                    return
            except:
                with open(writeFile, "w") as f:
                    f.write(currentData)
                    f.close()
                raise LinkedInRetrieverError("Deserialization failed. Invalid text stream")
    
    def validate(self, processedData: dict, strict: bool = False) -> bool:
        goodRating = True

        for validationFeature in self.VALIDATION_FEATURES:
            if validationFeature not in processedData.keys():
                print(f"Feature '{validationFeature}' missing from data")
                goodRating = False

                if strict:
                    raise LinkedInRetrieverError(f"Validation failed. Feature '{validationFeature}' missing")
            else:
                if processedData.get(validationFeature) == {} or processedData.get(validationFeature) == [] or processedData.get(validationFeature) == '':
                    print(f"Feature '{validationFeature}' exists but is empty")
                    goodRating = False

                    if strict:
                        raise LinkedInRetrieverError(f"Validation failed. Existing feature '{validationFeature}' is empty")
                    
                else:
                    print(f"Feature '{validationFeature}' is OK")
        
        return goodRating



if __name__ == "__main__":
    # profile = "https://www.linkedin.com/in/kevinliao2003"
    profile = "https://www.linkedin.com/in/cgnorthcutt/"

    retriever = LinkedInRetriever()
    data = retriever.retrieve(profile=profile)

    # retriever.print_keys(data)
    processed = retriever.clean_data(preprocessed=data)
    retriever.validate(processedData=processed)

    # retriever.print_keys(processed)
    retriever.save(processedDataset=processed, writeFolder=os.getcwd(), writeFile="cgnorthcutt", erase=True)