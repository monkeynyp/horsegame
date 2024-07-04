def find_occurrences_and_next_numbers(history, target_sequence):
    occurrences = []
    next_numbers = []

    for i in range(len(history) - len(target_sequence) + 1):
        if history[i:i + len(target_sequence)] == target_sequence:
            occurrences.append(i)
            next_numbers.append(history[i + len(target_sequence)])

    return occurrences, next_numbers

# Example usage:
historical_data = [10, 21, 4, 5, 6, 7, 9, 10, 11, 2, 9, 22,17,12,15,7,9,10,4,15,12,13,4,1,2]
target_sequence = [7, 9, 10]

occurrences, next_numbers = find_occurrences_and_next_numbers(historical_data, target_sequence)

print("Occurrences at indices:", occurrences)
print("Next numbers after each occurrence:", next_numbers)