"""Per-process request budget for a trusted server connection, never a public cache."""
import copy
import math
import threading
import time
from collections import OrderedDict
from urllib.parse import urlsplit


class XanoCrudError(Exception):
    pass


class XanoRateLimited(XanoCrudError):
    def __init__(self, retry_after=20):
        try:
            seconds=float(retry_after)
            if not math.isfinite(seconds):seconds=20
        except (ValueError,TypeError):seconds=20
        self.retry_after=max(20,math.ceil(seconds))
        super().__init__(f"Limite temporário do Xano. Aguarde {self.retry_after} segundos antes de tentar novamente. Não repita o cadastro sem conferir se ele foi salvo.")


class RequestBudget:
    def __init__(self, ttl=30.0, interval=2.1, clock=time.monotonic, sleep=time.sleep):
        self.ttl,self.interval,self.clock,self.sleep=ttl,interval,clock,sleep
        self.lock=threading.RLock()
        self.cache=OrderedDict()
        self.next_call=0.0
        self.cooldown=0.0

    def run(self, key, method, operation):
        with self.lock:
            now=self.clock()
            if now < self.cooldown:
                raise XanoRateLimited(self.cooldown-now)
            for old in [k for k,(expires,_) in self.cache.items() if expires <= now]:
                del self.cache[old]
            if method=='GET' and key in self.cache:
                return copy.deepcopy(self.cache[key][1])
            if method!='GET':self.cache.clear()
            delay=self.next_call-now
            if delay>0:self.sleep(delay)
            try:
                result=operation()
            except XanoRateLimited as exc:
                self.cache.clear()
                self.cooldown=self.clock()+exc.retry_after
                raise
            finally:
                self.next_call=self.clock()+self.interval
            if method=='GET':
                self.cache[key]=(self.clock()+self.ttl,copy.deepcopy(result))
                while len(self.cache)>128:self.cache.popitem(last=False)
            return copy.deepcopy(result)


_budgets={}
_guard=threading.Lock()

def budget_for(base_url):
    origin=urlsplit(base_url).netloc.lower()
    with _guard:
        return _budgets.setdefault(origin,RequestBudget())
