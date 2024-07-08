def find_occurrences_and_next_numbers(history, target_sequence):
    occurrences = []
    next_numbers = []
    print("In Function:",target_sequence)

    for shift in [-3,-2,-1,0,1,2,3]:
        target=[num + shift for num in target_sequence]
        print("In Function1:",target)

        for i in range(len(history) - len(target) + 1):
            if history[i:i + len(target)] == target: #Find the seq mactch
                occurrences.append(i)
                print("i:",i)
                if i < (len(history)-len(target)):
                    if history[i+len(target)]+shift>0:
                        next_numbers.append(history[i + len(target)]+shift)
    return occurrences, next_numbers     

# Example usage:
historical_data = [10, 21, 4, 5, 6, 7, 9, 10, 11, 2, 9, 22, 17, 12, 15, 7, 9, 10, 4, 15, 12, 13, 4, 1, 2, 7, 9, 10, 11,8,10,11,5, 5,7,8,12,6,8,9,1,4]
target_sequence = [7, 9, 10]

occurrences, next_numbers = find_occurrences_and_next_numbers(historical_data, target_sequence)

print("Occurrences at indices:", occurrences)
print("Next numbers after each occurrence:", next_numbers)