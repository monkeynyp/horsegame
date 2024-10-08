# Step 1: Add 1 to all values in the dataset
data = [
    (0, 1, 2, 3, 4, 5), (0, 1, 2, 6, 7, 8), (0, 1, 2, 9, 10, 11), (0, 1, 2, 12, 13, 14), (0, 1, 4, 6, 8, 14), 
    (0, 2, 4, 10, 12, 13), (0, 3, 4, 6, 10, 13), (0, 3, 4, 7, 8, 12), (0, 3, 4, 9, 11, 14), (0, 3, 5, 9, 10, 13), 
    (0, 5, 6, 9, 11, 12), (0, 5, 7, 8, 10, 14), (0, 7, 8, 9, 11, 13), (1, 2, 3, 7, 11, 12), (1, 2, 5, 6, 8, 9), 
    (1, 3, 5, 6, 13, 14), (1, 3, 5, 7, 10, 11), (1, 3, 5, 8, 9, 12), (1, 4, 6, 10, 11, 12), (1, 4, 7, 9, 13, 14), 
    (1, 8, 10, 11, 13, 14), (2, 3, 6, 7, 9, 13), (2, 3, 8, 10, 12, 14), (2, 4, 5, 6, 7, 10), (2, 4, 5, 8, 11, 13), 
    (2, 4, 5, 9, 12, 14), (2, 6, 7, 11, 12, 14), (3, 4, 5, 7, 11, 14), (3, 6, 8, 11, 12, 13), (4, 6, 8, 9, 10, 14), 
    (5, 7, 9, 10, 12, 13), (15, 16, 17, 18, 19, 20), (15, 16, 20, 23, 24, 25), (15, 16, 21, 27, 28, 29), (15, 16, 22, 26, 29, 30), 
    (15, 17, 18, 21, 22, 25), (15, 17, 18, 23, 27, 29), (15, 17, 18, 24, 26, 28), (15, 17, 24, 25, 29, 30), (15, 18, 20, 24, 28, 30), 
    (15, 18, 21, 23, 26, 30), (15, 19, 20, 21, 24, 29), (15, 19, 22, 23, 25, 28), (15, 19, 25, 26, 27, 30), (15, 20, 22, 24, 26, 27), 
    (16, 17, 20, 22, 28, 29), (16, 17, 21, 24, 27, 30), (16, 17, 23, 25, 26, 27), (16, 18, 20, 21, 26, 27), (16, 18, 22, 23, 24, 29), 
    (16, 18, 23, 25, 28, 30), (16, 19, 21, 22, 23, 27), (16, 19, 22, 25, 27, 29), (16, 19, 24, 26, 28, 30), (16, 20, 21, 22, 25, 30), 
    (16, 20, 23, 27, 29, 30), (17, 18, 22, 27, 28, 30), (17, 19, 20, 24, 26, 30), (17, 19, 20, 25, 27, 28), (17, 19, 21, 22, 26, 29), 
    (17, 19, 22, 23, 24, 30), (17, 20, 21, 23, 24, 28), (18, 19, 20, 22, 23, 26), (18, 19, 21, 23, 25, 29), (18, 19, 21, 24, 25, 27), 
    (18, 19, 21, 28, 29, 30), (18, 20, 25, 26, 28, 29), (21, 22, 24, 25, 26, 28), (23, 24, 26, 27, 28, 29), (31, 32, 33, 34, 35, 36), 
    (31, 32, 37, 38, 39, 40), (31, 32, 41, 42, 43, 44), (31, 32, 45, 46, 47, 48), (31, 33, 37, 42, 43, 45), (31, 33, 38, 44, 46, 47), 
    (31, 33, 39, 40, 41, 48), (31, 34, 37, 41, 46, 47), (31, 34, 38, 42, 43, 48), (31, 34, 39, 40, 44, 45), (31, 35, 36, 37, 44, 48), 
    (31, 35, 36, 38, 41, 45), (31, 35, 39, 42, 46, 47), (31, 35, 40, 42, 43, 46), (31, 36, 39, 42, 43, 47), (31, 36, 40, 43, 46, 47), 
    (32, 33, 34, 39, 43, 46), (32, 33, 34, 40, 42, 47), (32, 33, 37, 41, 44, 45), (32, 33, 38, 44, 45, 48), (32, 34, 37, 41, 45, 48), 
    (32, 34, 38, 41, 44, 48), (32, 35, 37, 38, 43, 47), (32, 35, 39, 42, 45, 48), (32, 35, 40, 41, 44, 46), (32, 36, 37, 38, 42, 46), 
    (32, 36, 39, 41, 44, 47), (32, 36, 40, 43, 45, 48), (33, 34, 37, 38, 41, 44), (33, 34, 37, 38, 45, 48), (33, 35, 37, 40, 45, 46), 
    (33, 35, 38, 39, 42, 44), (33, 35, 41, 43, 47, 48), (33, 36, 37, 39, 45, 47), (33, 36, 38, 40, 43, 44), (33, 36, 41, 42, 46, 48), 
    (34, 35, 37, 39, 41, 42), (34, 35, 38, 40, 46, 48), (34, 35, 43, 44, 45, 47), (34, 36, 37, 40, 41, 43), (34, 36, 38, 39, 47, 48), 
    (34, 36, 42, 44, 45, 46), (35, 36, 39, 40, 42, 43), (35, 36, 39, 40, 46, 47), (37, 39, 43, 44, 46, 48), (37, 40, 42, 44, 47, 48), 
    (38, 39, 41, 43, 45, 46), (38, 40, 41, 42, 45, 47)
]

data = [tuple(x+1 for x in row) for row in data]

# Step 2: Function to get user input and validate against dataset
def validate_user_input(data):
    user_input = input("Enter six numbers separated by spaces: ").split()
    user_numbers = tuple(map(int, user_input))
    
    matching_combinations = []
    
    for combination in data:
        match_count = len(set(combination) & set(user_numbers))
        if match_count > 2:
            matching_combinations.append(combination)
    
    if matching_combinations:
        print("Matching combinations:")
        for match in matching_combinations:
            print(match)
    else:
        print("No matching combinations found.")

# Run the validation function
validate_user_input(data)