import nltk; nltk.download('popular')

"""
Source: Otten, Jennifer J, et al. “Dietary Reference Intakes: The Essential Guide to Nutrient Requirements.” National Academies Press: OpenBook, 2006, www.nap.edu/read/11537/chapter/1#xii.  
"""

# Essential Vitamins for Females (all in milligrams): {"Age Range": (daily required intake)}
f_vitamin_a = {"Infant": 0.500,"1-3": 0.300, "4-8": 0.400, "9-13": 0.600, "14-18": 0.700, "19-30": 0.700, "31-50": 0.700, "51-70": 0.700, "71+": 0.700, "Preg. <= 18": 0.750, "Preg. 19+": 0.770, "Lact. <= 18": 1.2, "Lact. 19+": 1.3}
f_vitamin_b_6 = {"Infant": 0.300, "1-3": 0.500, "4-8": 0.600, "9-13": 1.000, "14-18": 1.300, "19-30": 1.300, "31-50": 1.300, "51-70": 1.700, "71+": 1.700, "Preg. <= 18": 1.900, "Preg. 19+": 1.900, "Lact. <= 18": 2.000, "Lact. 19+": 2.000}
f_vitaminb_b_12 = {"Infant": 0.0005, "1-3": 0.0009, "4-8": 0.0012, "9-13": 0.0018, "14-18": 0.0024, "19-30": 0.0024, "31-50": 0.0024, "51-70": 0.0024, "71+": 0.0024, "Preg. <= 18": 0.0026, "Preg. 19+": 0.0026, "Lact. <= 18": 0.0028, "Lact. 19+": 0.0028}
f_vitamin_c = {"Infant": 45,"1-3": 15, "4-8": 25, "9-13": 45, "14-18": 65, "19-30": 75, "31-50": 75, "51-70": 75, "71+": 75, "Preg. <= 18": 80, "Preg. 19+": 85, "Lact. <= 18": 115, "Lact. 19+": 120}
f_vitamin_d = {"Infant": 0.015,"1-3": 0.0275, "4-8": 0.0275, "9-13": 0.0275, "14-18": 0.0275, "19-30": 0.0275, "31-50": 0.0275, "51-70": 0.030, "71+": 0.0325, "Preg. <= 18": 0.0275, "Preg. 19+": 0.0275, "Lact. <= 18": 0.0275, "Lact. 19+": 0.0275}
f_vitamin_e = {"Infant": 5.000,"1-3":  6.000, "4-8":  7.000, "9-13": 11.000, "14-18": 15.000, "19-30": 15.000, "31-50": 15.000, "51-70": 15.000, "71+": 15.000, "Preg. <= 18": 15.000, "Preg. 19+": 15.000, "Lact. <= 18": 19.000, "Lact. 19+": 19.000}


# Essential Minerals for Females (all in milligrams): {"Age Range": (daily required intake)
f_calcium = {"Infant": 240,"1-3": 500, "4-8": 800, "9-13": 1300, "14-18": 1300, "19-30": 1000, "31-50": 1000, "51-70": 1200, "71+": 1200, "Preg. <= 18": 1300, "Preg. 19+": 1000, "Lact. <= 18": 1300, "Lact. 19+": 1000}
f_iron = {"Infant": 11.000, "1-3": 7.000, "4-8": 10.000, "9-13": 8.000, "14-18": 15.000, "19-30": 18.000, "31-50": 18.000, "51-70": 8.000, "71+": 8.000, "Preg. <= 18": 27.000, "Preg. 19+": 27.000, "Lact. <= 18": 10.000, "Lact. 19+": 9.000}
f_magnesium = {"Infant": 75.000,"1-3": 80.000, "4-8": 130.000, "9-13": 240.000, "14-18": 360.000, "19-30": 310.000, "31-50": 320.000, "51-70": 320.000, "71+": 320.000, "Preg. <= 18": 400.000, "Preg. 19+": 350.000, "Lact. <= 18": 360.000, "Lact. 19+": 310.000}
f_potassium = {"Infant": 550.000,"1-3": 3000.000, "4-8": 3800.000, "9-13": 4500.000, "14-18": 4700.000, "19-30": 4700.000, "31-50": 4700.000, "51-70": 4700.000, "71+": 4700.000, "Preg. <= 18": 4700.000, "Preg. 19+": 4700.000, "Lact. <= 18": 5100.000, "Lact. 19+": 5100.000}
f_zinc = {"Infant": 3.000,"1-3": 3.000, "4-8": 5.000, "9-13": 8.000, "14-18": 9.000, "19-30": 8.000, "31-50": 8.000, "51-70": 8.000, "71+": 8.000, "Preg. <= 18": 12.000, "Preg. 19+": 11.000, "Lact. <= 18": 13.000, "Lact. 19+": 12.000}

# Creates a user 
class User:
    def __init__(self, name=str, age=int, height=int, weight=int, pregnancy_status=str, breastfeeding_status=str, user_symptoms=str):
        self.name = name
        self.age = age
        self.height = height
        self.weight = weight
        self.pregnancy_status = pregnancy_status
        self.breastfeeding_status = breastfeeding_status
        self.age_range = self.compute_age_range()
        
        self.user_vitamin_a = f_vitamin_a[self.age_range]
        self.user_vitamin_b_6 = f_vitamin_b_6[self.age_range]
        self.user_vitamin_b_12 = f_vitaminb_b_12[self.age_range]
        self.user_vitamin_c = f_vitamin_c[self.age_range]
        self.user_vitamin_d = f_vitamin_d[self.age_range]
        self.user_vitamin_e = f_vitamin_e[self.age_range]

        
        self.user_calcium = f_calcium[self.age_range]
        self.user_iron = f_iron[self.age_range]
        self.user_magnesium = f_magnesium[self.age_range]
        self.uesr_potassium = f_potassium[self.age_range]
        self.user_zinc = f_zinc[self.age_range]
        
    
    def compute_age_range(self):
        """Figures out an age range for the user"""
      
        # Factors in Pregnancy and Lactation
        if self.pregnancy_status == "Y" or self.breastfeeding_status == "Y":
            
            # If both pregnant and lactating, simulation assumes lactation label
            if self.pregnancy_status == "Y" and self.breastfeeding_status == "Y":
                if self.age <= 18: 
                    self.age_range = "Lact. <= 18"
                else:
                    self.age_range = "Lact. 19+" 
            
            # Checks age and pregnancy status
            if self.pregnancy_status == "Y":
                if self.age <= 18:
                    self.age_range = "Preg. <= 18"
                else: 
                    self.age_range = "Preg. 19+"
            
            # Checks age and lactation status
            if self.breastfeeding_status == "Y":
                if self.age <= 18:
                    self.age_range = "Lact. <= 18"
                else: 
                    self.age_range = "Lact. 19+"
            
        else:
            # Checks if user is in the age range of 1 to 3
            if self.age < 0 & self.age >= 3:
                self.age_range = "1-3"
        
            # Checks if user is in the age range of 4 to 8
            if self.age >= 4 & self.age <= 8:
                self.age_range = "4-8"
        
            # Checks if user is in the age range of 9 to 13
            if self.age >= 9 & self.age <= 13:
                self.age_range = "9-13"
        
            # Checks if user is in the age range of 14 to 18
            if self.age >= 14 & self.age <= 18:
                self.age_range = "14-18"

            # Checks if user is in the age range of 19 to 30
            if self.age >= 19 & self.age <= 30:
                self.age_range = "19-30"
        
            # Checks if user is in the age range of 31 to 50
            if self.age >= 31 & self.age <= 50:
                self.age_range = "31-50"
        
            # Checks if user is in the age range of 51 to 70
            if self.age >= 51 & self.age <= 70:
                self.age_range = "51-70"
        
            # Checks if user is in the age range of 71+
            if self.age >= 71:
                self.age_range = "71+"
        
        return self.age_range

    def get_status(self):
        
        """Returns the basic information of the user"""

        status = """
-----------------GENERAL USER INFO-----------------
                 Name: {name}
                 Age: {age}
                 Age Range: {age_range}
                 Height: {height}
                 Weight: {weight}
                 Pregnancy Status: {pregnancy_status}
                 Breastfeeding Status: {breastfeeding_status}

-----------------USER'S RECOMMENDED DAILY VITAMIN AND MINERAL COUNT-------------
                                (in milligrams, mg)
                 Vitamin A: {user_vitamin_a}
                 Vitamin B6: {user_vitamin_b_6}
                 Vitamin B12: {user_vitamin_b_12}
                 Vitamin C: {user_vitamin_c}
                 Vitamin D: {user_vitamin_d}
                 Vitamin E: {user_vitamin_e}
                 
                 Calcium: {user_calcium}
                 Iron: {user_iron}
                 Magnesium: {user_magnesium}
                 Potassium: {user_potassium}
                 Zinc: {user_zinc}
                 """
        return status.format(name=self.name, age=self.age, age_range=self.age_range, height=self.height, weight=self.weight, pregnancy_status=self.pregnancy_status, 
        breastfeeding_status=self.breastfeeding_status, user_vitamin_a=self.user_vitamin_a,
        user_vitamin_b_6=self.user_vitamin_b_6, user_vitamin_b_12=self.user_vitamin_b_12, user_vitamin_c=self.user_vitamin_c, user_vitamin_d=self.user_vitamin_d, user_vitamin_e=self.user_vitamin_e,
        user_calcium=self.user_calcium, user_iron=self.user_iron, user_magnesium=self.user_magnesium, user_potassium=self.uesr_potassium, user_zinc=self.user_zinc)
        

# Asks survey questions and calls on functions that will narrow down data and deficencies
def main():
    # Gets user information through a series of questions
    print("Welcome to VitaminSHE!")
   
    user_name = input("What is your name? ")
    
    user_age = int(input("How old are you? "))
   
    # Checks if user_age is a valid input
    while user_age <= 0:
        print("Invalid Entry.")
        user_age = int(input("What is your name? "))

    user_height = input("What is your height (Please round to the nearest whole inch)? ")
    user_weight = input("What is your weight? (Please round to the nearest whole pound)? ")

    pregnancy_status = input("Are you pregnant (Y or N)? ")
    pregnancy_status = pregnancy_status.upper()

    # Checks if pregnancy_status is a valid input
    while pregnancy_status != "Y" and pregnancy_status != "N":
        print("Invalid Entry.")
        pregnancy_status = input("Are you pregnant (Y or N)? ")
        pregnancy_status = pregnancy_status.upper()

    breastfeeding_status = input("Are you currently breastfeeding (Y or N)? ")
    breastfeeding_status = breastfeeding_status.upper()

    # Checks if breastfeeding_status is a valid input
    while breastfeeding_status != "Y" and breastfeeding_status != "N":
        print("Invalid Entry.")
        breastfeeding_status = input("Are you pregnant (Y or N)? ")
        breastfeeding_status = breastfeeding_status.upper()

    user = User(user_name, user_age, user_height, user_weight, pregnancy_status, breastfeeding_status)
    print(user.get_status())

main()
