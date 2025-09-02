import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

np.random.seed(1000)

y = np.random.standard_normal((1000,2))
c = np.random.randint(0,10,len(y))

# print(y, c)

fig, ax = plt.subplots(figsize=(10,6))
plt.boxplot(y, showfliers=False)
plt.setp(ax, xticklabels=['1st','2nd'])
plt.show()


# plt.figure(figsize=(10,6))
# plt.hist(y, stacked=True, bins=25, alpha=0.5)
# plt.show()

# y = np.random.standard_normal((20,2)).cumsum(axis=0)
# y[:,0] = y[:,0] * 100

# print(mpl.__version__)
# print(np.__version__)
# print(y[:50])



#Two y axises/one x axis

# fig, ax1 = plt.subplots()
# plt.plot(q[:,0],'b',lw=1.5, label='first')
# plt.plot(q[:,0],'ro')
# plt.legend(loc=0)
# plt.xlabel('index')
# plt.ylabel('value first')
# plt.title('A Simple Plot')
# ax2 = ax1.twinx()
# plt.plot(q[:,1],'g',lw=1.5, label='second')
# plt.plot(q[:,1],'ro')
# plt.legend(loc=0)
# plt.ylabel('value second')
# plt.show()

#Subplots - same plot styles

# plt.figure(figsize=(10,6))
# plt.subplot(211)
# plt.plot(y[:,0], 'r',lw=1.5, label='AAPL')
# plt.legend(loc=0)
# plt.ylabel('$/share')
# plt.title('APPL stock price 2000 - 2020')
# plt.subplot(212)
# plt.plot(y[:,1],'b', label='GOO')
# plt.legend(loc=0)
# plt.ylabel('$/share')
# plt.xlabel('t')
# plt.show()

#Subplots - different plot styles

# plt.figure(figsize=(10,6))
# plt.subplot(121)
# plt.plot(y[:,0], 'r',lw=1.5, label='AAPL')
# plt.legend(loc=0)
# plt.ylabel('$/share')
# plt.xlabel('t')
# plt.title('APPL stock price 2000 - 2020')
# plt.subplot(122)
# plt.bar(np.arange(len(y)), y[:,1],color='b', label='Std')
# plt.legend(loc=0)
# plt.xlabel('t')
# plt.title('APPL price deviation 2000 - 2020')
# plt.show()

