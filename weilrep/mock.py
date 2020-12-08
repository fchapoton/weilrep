r"""

Sage code for vector-valued quasimodular forms and mock modular forms

AUTHORS:

- Brandon Williams

"""

# ****************************************************************************
#       Copyright (C) 2020 Brandon Williams
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************


from sage.functions.other import floor
from sage.rings.big_oh import O
from sage.rings.rational_field import QQ

from .weilrep_modular_forms_class import WeilRepModularForm

class WeilRepQuasiModularForm(WeilRepModularForm):
    r"""
    Class for quasimodular forms.

    A quasimodular form is the holomorphic part of an almost-holomorphic modular form i.e. a function f that satisfies modular transformations and has the expansion
    f(\tau) = f_0(\tau) + f_1(\tau) (4\pi y)^(-1) + ... + f_r(\tau) (4 \pi y)^(-r)

    A WeilRepQuasiModularForm instance is constructed using
    WeilRepQuasiModularForm(k, S, list_f)
    by providing
    - ``k `` -- the weight
    - ``S`` -- the gram matrix
    - ``list_f`` -- a list of WeilRepModularForm's f_r, ..., f_1, f_0

    This represents the form f_0(\tau) + f_1(\tau) (4\pi y)^(-1) + ... + f_r(\tau) (4 \pi y)^(-r).

    A WeilRepQuasiModularForm instance acts as the WeilRepModularForm f_0 (which is a quasimodular form).
    """

    def __init__(self, k, S, terms, weilrep=None):
        l = len(terms)
        try:
            j = next(j for j, x in enumerate(terms) if x)
        except StopIteration:
            j = l
        f = terms[-1].fourier_expansion()
        super().__init__(k, S, f, weilrep=weilrep)
        l -= 1
        if j < l:
            self.__class__ = WeilRepQuasiModularForm
            self.__terms = terms[j:]
            self.__depth = l - j

    def __add__(self, other):
        r"""
        Add quasimodular forms.
        """
        if not other:
            return self
        S1 = self.gram_matrix()
        S2 = other.gram_matrix()
        if S1 != S2:
            raise ValueError('Incompatible Gram matrices')
        if self.weight() != other.weight():
            raise ValueError('Incompatible weights')
        d1 = self.depth()
        d2 = other.depth()
        i = d1 <= d2
        t1 = self._terms()
        t2 = other._terms()
        j = d2-d1
        if i:
            X = t2[:j] + [t1[i]+t2[i+j] for i in range(d1 + 1)]
        else:
            X = t1[:-j] + [t1[i-j] + t2[i] for i in range(d2 + 1)]
        return WeilRepQuasiModularForm(self.weight(), S1, X, weilrep = self.weilrep())

    __radd__ = __add__

    def __sub__(self, other):
        r"""
        Subtract quasimodular forms.
        """
        if not other:
            return self
        S1 = self.gram_matrix()
        S2 = other.gram_matrix()
        if S1 != S2:
            raise ValueError('Incompatible Gram matrices')
        if self.weight() != other.weight():
            raise ValueError('Incompatible weights')
        d1 = self.depth()
        d2 = other.depth()
        i = d1 <= d2
        t1 = self._terms()
        t2 = other._terms()
        j = d2-d1
        if i:
            X = [-x for x in t2[:j]] + [t1[i]-t2[i+j] for i in range(d1 + 1)]
        else:
            X = t1[:-j] + [t1[i-j] - t2[i] for i in range(d2 + 1)]
        return WeilRepQuasiModularForm(self.weight(), S1, X, weilrep = self.weilrep())

    def __neg__(self):
        r"""
        Negative of quasimodular form
        """
        return WeilRepQuasiModularForm(self.weight(), self.gram_matrix(), [-x for x in self._terms()], weilrep=self.weilrep())

    def __mul__(self, other):
        r"""
        (Tensor) Product of quasimodular forms
        """
        if other in QQ:
            return WeilRepQuasiModularForm(self.weight(), self.gram_matrix(), [other*x for x in self._terms()], weilrep=self.weilrep())
        w1 = self.weilrep()
        w2 = other.weilrep()
        k = self.weight() + other.weight()
        w = w1 + w2
        t1 = self._terms()
        t2 = other._terms()
        r = self.depth()
        s = other.depth()
        rs = r + s
        j = k - rs - rs
        p = self.precision()
        X = [w.zero(i + i + j, p) for i in range(rs + 1)]
        for i in range(r + 1):
            for j in range(s + 1):
                X[i + j] += t1[i]*t2[j]
        return WeilRepQuasiModularForm(k, w.gram_matrix(), X, weilrep=w)

    __rmul__ = __mul__

    def __div__(self, other):
        r"""
        Division of quasimodular forms by scalars.
        """
        return WeilRepQuasiModularForm(self.weight(), self.gram_matrix(), [x/other for x in self._terms()], weilrep=self.weilrep())

    __truediv__ = __div__

    def __pow__(self, N):
        r"""
        Tensor power of quasimodular form with itself.
        """
        if N == 1:
            return self
        elif N > 1:
            Nhalf = floor(N / 2)
            return (self ** Nhalf) * (self ** (N - Nhalf))
        raise ValueError('Invalid exponent')

    def depth(self):
        r"""
        Computes the "depth" of the quasimodular form. 
        """
        try:
            return self.__depth
        except AttributeError:
            return 0

    def _terms(self):
        r"""
        Returns self's Taylor expansion in (4pi y)^(-1) as a list of WeilRepModularForm's.

        This should not be called directly because the terms in self's Taylor expansion are not modular forms (although we treat them as if they were).
        """
        try:
            return self.__terms
        except AttributeError:
            self.__class__ = WeilRepModularForm
            return [self]

    def completion(self):
        r"""
        Return self's completion to an almost-holomorphic modular form.

        EXAMPLES::
            sage: from weilrep import WeilRep
            sage: w = WeilRep([])
            sage: e2 = w.eisenstein_series(2, 5)
            sage: e2.completion()
            Almost holomorphic modular form f_0 + f_1 * (4 pi y)^(-1), where:
            f_0 =
            [(), 1 - 24*q - 72*q^2 - 96*q^3 - 168*q^4 + O(q^5)]
            --------------------------------------------------------------------------------
            f_1 =
            [(), -12 + O(q^5)]

            sage: from weilrep import WeilRep
            sage: w = WeilRep(matrix([[-2, 0], [0, -2]]))
            sage: r.<x, y> = PolynomialRing(ZZ)
            sage: f = w.theta_series(5, P = x^2)
            sage: f.completion()
            Almost holomorphic modular form f_0 + f_1 * (4 pi y)^(-1), where:
            f_0 =
            [(0, 0), 2*q + 4*q^2 + 8*q^4 + O(q^5)]
            [(1/2, 0), 1/2*q^(1/4) + q^(5/4) + 9/2*q^(9/4) + 9*q^(13/4) + q^(17/4) + O(q^(21/4))]
            [(0, 1/2), 4*q^(5/4) + 4*q^(13/4) + 16*q^(17/4) + O(q^(21/4))]
            [(1/2, 1/2), q^(1/2) + 10*q^(5/2) + 9*q^(9/2) + O(q^(11/2))]
            --------------------------------------------------------------------------------
            f_1 =
            [(0, 0), -1/2 - 2*q - 2*q^2 - 2*q^4 + O(q^5)]
            [(1/2, 0), -q^(1/4) - 2*q^(5/4) - q^(9/4) - 2*q^(13/4) - 2*q^(17/4) + O(q^(21/4))]
            [(0, 1/2), -q^(1/4) - 2*q^(5/4) - q^(9/4) - 2*q^(13/4) - 2*q^(17/4) + O(q^(21/4))]
            [(1/2, 1/2), -2*q^(1/2) - 4*q^(5/2) - 2*q^(9/2) + O(q^(11/2))]
        """
        X = [self]
        r = self.depth()
        j = 1
        for i in range(r):
            j *= (i + 1)
            X.append(X[-1].shift() / j)
        return WeilRepAlmostHolomorphicModularForm(self.weight(), self.gram_matrix(), X, weilrep = self.weilrep())

    def derivative(self):
        r"""
        Compute self's derivative. This is a quasimodular form whose depth is (usually) one greater than self.

        EXAMPLES::
            sage: from weilrep import WeilRep
            sage: w = WeilRep([])
            sage: e2 = w.eisenstein_series(2, 5)
            sage: e2.derivative()
            [(), -24*q - 144*q^2 - 288*q^3 - 672*q^4 + O(q^5)]
        """
        t = self._terms()
        S = self.gram_matrix()
        w = self.weilrep()
        R, q = self.fourier_expansion()[0][2].parent().objgen()
        def a(offset, f):
            if not f:
                return O(q ** f.prec())
            val = f.valuation()
            prec = f.prec()
            return (q**val * R([(i + offset) * f[i] for i in range(val, prec)])).add_bigoh(prec - floor(offset))
        def d(X):
            k = X.weight()
            Y = [(x[0], x[1], a(x[1], x[2])) for x in X.fourier_expansion()]
            return WeilRepModularForm(k + 2, S, Y, w)
        r = self.depth()
        k = self.weight()
        X = [(r - k) * t[0]] + [(r - k - j) * t[j] + d(t[j-1]) for j in range(1, r+1)] + [d(t[-1])]
        return WeilRepQuasiModularForm(k + 2, self.gram_matrix(), X, weilrep = self.weilrep())

    def shift(self):
        r"""
        Apply the "shift operator" on quasimodular forms. This is a quasimodular form whose depth is one less than self.

        EXAMPLES::
            sage: from weilrep import WeilRep
            sage: w = WeilRep([])
            sage: e2 = w.eisenstein_series(2, 5)
            sage: e2.shift()
            [(), -12 + O(q^5)]
        """
        r = self.depth()
        f = [1]*(r + 1)
        k = r - 1
        for j in range(1, r + 1):
            f[k] = j * f[k + 1]
            k -= 1
        X = self._terms()
        return WeilRepQuasiModularForm(k - 2, self.gram_matrix(), [f[i]*y for i, y in enumerate(X[:-1])], weilrep=self.weilrep())

class WeilRepAlmostHolomorphicModularForm:
    r"""
    Provide a custom string representation for the 'completion' of a quasimodular form. Also implements arithmetic operations and the Maass raising operator.

    Currently the only way to construct a WeilRepAlmostHolomorphicModularForm is as the modular completion of a quasimodular form.
    """
    def __init__(self, k, S, X, weilrep=None):
        self.__weight = k
        self.__gram_matrix = S
        self.__list = X
        if weilrep:
            self.__weilrep = weilrep
        self.__depth = X[0].depth()

    def __repr__(self):
        try:
            return self.__string
        except AttributeError:
            r = self.__depth
            X = self.__list
            s = 'Almost holomorphic modular form f_0'
            t = str(X[0])
            h = '\n'+'-'*80
            for i, x in enumerate(X):
                if i >= 1:
                    s, t = s + ' + f_%d * (4 pi y)^(-%d)'%(i, i), t + h + '\nf_%d =\n%s'%(i, str(x))
            x = s + ', where:\nf_0 =\n' + t
            self.__string = x
            return x

    def __getitem__(self, n):
        return self.__list[n]

    def __iter__(self):
        for x in self.__list:
            yield x

    ## lazy arithmetic ##

    def __add__(self, other):
        if not other:
            return self
        try:
            return (self[0] + other[0]).completion()
        except AttributeError:
            return (self[0] + other).completion()

    __radd__ = __add__

    def __sub__(self, other):
        if not other:
            return self
        try:
            return (self[0] - other[0]).completion()
        except AttributeError:
            return (self[0] - other).completion()

    def __mul__(self, other):
        try:
            if other in QQ:
                return (other * self[0]).completion()
            try:
                return (self[0] * other[0]).completion()
            except AttributeError:
                return (self[0] * other).completion()
        except TypeError:
            print('self:', self)

    __rmul__ = __mul__

    def __neg__(self):
        return (-self[0]).completion()

    def __div__(self, n):
        return (self[0] / n).completion()
    __truediv__ = __div__

    def __pow__(self, n):
        return (self[0]**n).completion()

    def derivative(self):
        return self[0].derivative().completion()

    def shift(self):
        return self[0].shift().completion()

class WeilRepMockModularForm(WeilRepModularForm):
    r"""
    Class for mock modular forms.
    """

    def __init__(self, k, S, X, shadow, weilrep = None):
        WeilRepModularForm.__init__(self, k, S, X, weilrep = weilrep)
        self.__class__ = WeilRepMockModularForm
        self.__shadow = shadow


    def shadow(self):
        return self.__shadow

    def __add__(self, other):
        f = super().__add__(other)
        s = self.shadow()
        if isinstance(other, WeilRepMockModularForm):
            s += other.shadow()
        return WeilRepMockModularForm(self.weight(), self.gram_matrix(), f.fourier_expansion(), s, weilrep = self.weilrep())

    def __sub__(self, other):
        f = super().__sub__(other)
        s = self.shadow()
        if isinstance(other, WeilRepMockModularForm):
            s -= other.shadow()
        return WeilRepMockModularForm(self.weight(), self.gram_matrix(), f.fourier_expansion(), s, weilrep = self.weilrep())

    def __neg__(self):
        return WeilRepMockModularForm(self.weight(), self.gram_matrix(), super().__neg__().fourier_expansion(), -self.shadow(), weilrep = self.weilrep())

    def __mul__(self, other):
        if other in QQ:
            f = super().__mul__(other)
            return WeilRepMockModularForm(self.weight(), self.gram_matrix(), f.fourier_expansion(), self.shadow() * other, weilrep = self.weilrep())
        return NotImplemented

    def __truediv__(self, other):
        return self.__mul__(~other)
    __div__ = __truediv__

    def derivative(self):
        return NotImplemented