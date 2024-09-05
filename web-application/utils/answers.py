# Question 1: Palindrome Number
# Given an integer x, return true if x is a palindrome, and false otherwise.
def is_palindrome(x):
    if x < 0:
        return False
    return str(x) == str(x)[::-1]

# Test cases for Palindrome Number
# 121 -> true
# -121 -> false
# 10 -> false


# Question 2: Reverse Integer
# Given a signed 32-bit integer x, return x with its digits reversed. If reversing x causes the value to go outside the signed 32-bit integer range [-231, 231 - 1], then return 0.
def reverse_integer(x):
    INT_MAX = 2**31 - 1
    INT_MIN = -2**31

    sign = 1 if x > 0 else -1
    x = abs(x)
    reversed_x = 0

    while x != 0:
        pop = x % 10
        x //= 10
        if reversed_x > INT_MAX // 10 or (reversed_x == INT_MAX // 10 and pop > 7):
            return 0
        if reversed_x < INT_MIN // 10 or (reversed_x == INT_MIN // 10 and pop > 8):
            return 0
        reversed_x = reversed_x * 10 + pop

    return sign * reversed_x

# Test cases for Reverse Integer
# 123 -> 321
# -123 -> -321
# 1534236469 -> 0


# Question 3: Valid Parentheses
# Given a string containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.
def is_valid_parentheses(s):
    stack = []
    mapping = {")": "(", "}": "{", "]": "["}

    for char in s:
        if char in mapping:
            top_element = stack.pop() if stack else '#'
            if mapping[char] != top_element:
                return False
        else:
            stack.append(char)
    return not stack

# Test cases for Valid Parentheses
# "()" -> true
# "()[]{}" -> true
# "(]" -> false


# Question 4: Longest Valid Parentheses
# Given a string containing just the characters '(' and ')', find the length of the longest valid (well-formed) parentheses substring.
def longest_valid_parentheses(s):
    max_length = 0
    stack = [-1]

    for i in range(len(s)):
        if s[i] == '(':
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)
            else:
                max_length = max(max_length, i - stack[-1])
    return max_length

# Test cases for Longest Valid Parentheses
# "(()" -> 2
# ")()())" -> 4
# "" -> 0


# Question 5: Container With Most Water
# Given n non-negative integers a1, a2, ..., an, where each represents a point at coordinate (i, ai). Find two lines, which together with x-axis forms a container, such that the container contains the most water.
def max_area(height):
    left, right = 0, len(height) - 1
    max_water = 0

    while left < right:
        width = right - left
        max_water = max(max_water, min(height[left], height[right]) * width)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1

    return max_water

# Test cases for Container With Most Water
# [1,8,6,2,5,4,8,3,7] -> 49
# [1,1] -> 1
# [4,3,2,1,4] -> 16