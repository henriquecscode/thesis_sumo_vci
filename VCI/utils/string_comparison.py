def levenshtein_similarity(str1: str, str2: str) -> float:
    len_str1 = len(str1) + 1
    len_str2 = len(str2) + 1

    # Create a matrix to store distances
    matrix = [[0 for _ in range(len_str2)] for _ in range(len_str1)]

    # Initialize the matrix
    for i in range(len_str1):
        matrix[i][0] = i
    for j in range(len_str2):
        matrix[0][j] = j

    # Calculate the Levenshtein distance
    for i in range(1, len_str1):
        for j in range(1, len_str2):
            cost = 0 if str1[i - 1] == str2[j - 1] else 1
            matrix[i][j] = min(
                matrix[i - 1][j] + 1,      # Deletion
                matrix[i][j - 1] + 1,      # Insertion
                matrix[i - 1][j - 1] + cost  # Substitution
            )

    # Return the similarity value
    max_len = max(len(str1), len(str2))
    similarity = 1 - (matrix[len_str1 - 1][len_str2 - 1] / max_len)
    return similarity