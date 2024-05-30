def calculate_total_aggregate(compulsory_data, optional_data):
    compulsory_grades = [min(float(grade) if grade else 4, 4) for grade in compulsory_data.values()]
    optional_grades = [min(float(grade) if grade else 4, 4) for grade in optional_data.values()]

    compulsory_grades.sort()
    optional_grades.sort()

    compulsory_sum = sum(compulsory_grades[:3])
    optional_sum = sum(optional_grades[:3])

    total_aggregate = compulsory_sum + optional_sum
    return total_aggregate
