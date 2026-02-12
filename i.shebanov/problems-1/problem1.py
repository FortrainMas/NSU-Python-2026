def cumulative_sum(arr):
    result = [0]
    for el in arr:
        result.append(result[-1] + el)
    return result
