# put your code here
def summ(number):
    generator = sum(int(digits) for digits in str(number))
    print(generator)


number = int(input())
summ(number)
