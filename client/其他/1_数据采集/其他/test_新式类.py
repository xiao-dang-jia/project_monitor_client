# -*- coding:utf-8 -*-

# 新式类对象可以直接通过__class__属性获取自身类型:type


# -*- coding:utf-8 -*-
class A(object):
    """
    新式类
    作为所有类的基类
    """

    def foo(self):
        print "class A"


class A1():
    """
    经典类
    作为所有类的基类
    """

    def foo(self):
        print "class A1"


class C(A):
    pass


class C1(A1):
    pass


class D(A):
    def foo(self):
        print "class D"


class D1(A1):
    def foo(self):
        print "class D1"


class E(C, D):
    pass


class E1(C1, D1):
    pass

# C->D->A
e = E()
e.foo()

e1 = E1()
e1.foo()