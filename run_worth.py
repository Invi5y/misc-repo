import worth
for i in range(20):
    me = worth.Person('Fabian')
    #print(me.name,
     #   me.today)

    y = 1992 #int(input('Provide your year of birth '))
    m = 2    #int(input('Provide your month of birth '))
    d = 29   #int(input('Provide you day of birth '))

    me.last_day(y,m,d)

    print(me.date_of_birth,
        me.last_day)