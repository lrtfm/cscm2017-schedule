#!python
from __future__ import print_function
import json, sys
from datetime import timedelta, datetime

reload(sys) 
sys.setdefaultencoding('utf-8')

labels, alabels = {}, {}
flag = 0
timedict = {"prof":20, "asprof":20, "lect":15, "stu":15, "other":15, "default": 20}
titlerank = {"prof":1, "asprof":2, "lect":3, "stu":4, "other":3, "default": 3}

class Bunch(object):
	def __init__(self, adict):
		self.__dict__.update(adict)

def saveData( var, filename ):
	json.dump(var, open(filename, 'w'))

def loadData( filename ):
	return json.load(open(filename, 'r'))

def idx_name( _, i ): return "{%s}\index{%s@%s}" % (_, i, _)

def npuwordvar( word, var ):
    hoge = "\\npu%s" % word
    for _ in var:
        hoge += "{%s}" % _
    return hoge
  
def npuauthor( uid, name, index ):
  return npuwordvar("author", [uid, name, index])

def npuauthornew( uid, name, num, tituly, index):
  return npuwordvar("authornew", [uid, name, num, tituly, index])

def npuauthorschool( name, school, index ):
  return npuwordvar("authorschool", [name, school, index])

def npufootauthor( author, name, school, email):
  return npuwordvar("footauthor", [name, school, email, author])

def npureport( title, label, name, school, time, index):
  return npuwordvar("report", [title, label, name, school, time, index])

def nputime(date, time):
  return npuwordvar("time", [date, time])

def nputitle( title, alabel ):
  return npuwordvar("title", [title, alabel])

def npuabstract( title, label, author, abst ):
  return npuwordvar("abstract", [title, label, author, abst])

def npufootstart( author, name, index):
  return npuwordvar("footstart", [name, author, index])

def npufootend(name, school, email):
  return npuwordvar("footend", [name, school, email])

def npuabstractnew( title, label, author, abst, what ):
  return npuwordvar("abstract", [title, label, author, abst, what])

def specialtable_inner( names, times ):
  per = 4
  reminder = len(names) % per
  if reminder > 0: reminder = per - reminder
  emptycells = ["" for _ in range(reminder)]
  names.extend(emptycells)
  times.extend(emptycells)

  ret = "";
  for _ in range((len(names) - 1) // per + 1):
    task = min(len(names), (_ + 1) * per)
    ret += "%%\n\t\\specialtable{%%\n\t"
    ret += " & ".join(names[_ * per:task])
    ret += "%%\n\t}{%%\n\t"
    ret += " & ".join(times[_ * per:task])
    ret += "%%\n\t}%%\n"
  return ret
 
def formattime(time):
  return time.strftime("%H:%M")

def str2time(str):
  [h, m] = str.split(":")
  return datetime(year=2017, month=7, day=21, hour=int(h), minute=int(m))

def getreporttime(starttime, l):
  tmpend = starttime + timedelta(minutes=l)
  return (tmpend, formattime(starttime) + "-" + formattime(tmpend))

def gethostsattr(i):
  attr = "organizors"
  if hasattr(i, "hosts"):
    attr = "hosts"
  return attr

def getreport(rlist, uid):
  for i in rlist:
    try:
      if int(i["usershowid"]) == int(uid):
        return i
    except KeyError as ke:
      print("keyerror: %s,%s" %(i, uid))
      return None
  else:
    print("uid:%s not found!" % uid)
    return None;

def makereportfake(rlist, j):
    uid_time = j.split(",")
    uid = uid_time[0]
    return getreport(rlist, uid)

def makereport(rlist, j, tmpstart):
    uid_time = j.split(",")
    uid = uid_time[0]
    one = getreport(rlist, uid)
    if uid=="10701":
        print(j, uid_time)
    if one != None:
        hoge = gettituly(one)
        t = int(uid_time[1]) if len(uid_time) > 1 else timedict.get(hoge, 20)
        tmpstart, one["time"] = getreporttime(tmpstart, t)

    return (one, tmpstart)

def gethostslist(reports):
    hosts = list()
    n = min(len(reports), 3)
    fullindex = [2, 0, 1]
    index = fullindex[3-n:3]

    for i in index:
        one = { "name": reports[i]["name"], "school": reports[i]["school"], "index": getindex(reports[i]) }
        hosts.append(one)
    return hosts

def gettopic(tid, topic_list):
  for i in topic_list:
    name = i["topic_name"].split(" ")
    if name[0] == tid:
      return i

  print("%s not found"% tid)
  return None

def npuleaderlist(i):
  ret = ""
  sep = "\\\\\n\t"
  attr = gethostsattr(i)
  ret = npuwordvar("leader", [ "\\cn"+attr,
    "\t" + sep.join([npuauthorschool(_["name"], _["school"], getindex(_)) for _ in getattr(i, attr)])])
  return ret



def gettituly(j):
  if j.has_key("tituly"):
    return j["tituly"]

  return ""

def getindex(j):
  if j.has_key("index"):
    return j["index"]
  return j["name"]

def ppreprocess(sess, topic_list):
  ret = list()
  for e in sess:
    ne = list()
    for i in range(0, len(e.topics)):
      tid = e.topics[i].split(",");

      one = gettopic(tid[0], topic_list)
      if one != None:
        if len(tid) > 1:
          one["room"] = tid[1]
        ne.append(one)
    e.topics = ne
    ret.append(e)

  return ret

def presort( sess, rlist ):
  ret = list()
  for e in sess:
    starttime = str2time(e.start_time)
    ne = list()
    for i in e.topics:
      new = list()
      reports = i["reports"]
      tmpend = tmpstart = starttime
      for j in reports:
        one = makereportfake(rlist, j)
        if one != None:
            one["j"] = j
            new.append(one)
      if i["topic_name"][0] == "T":
        new.sort(key=lambda obj:titlerank[obj.get('tituly', 'lect')], reverse=False) 

      for j in new:
        (j, tmpstart) = makereport(rlist, j["j"], tmpstart)

      i["reports"] = new
      if "hosts" in i:
        hosts = gethostslist(new)
        i["hosts"] = hosts
      ne.append(i)
    e.topics = ne
    ret.append(e)

  return ret

def shortlist( sess ):
  global labels, alabels, flag
  for e in sess:
    print("\session{%s}{%s}" % (e.session_name, e.date))
    starttime = str2time(e.start_time)
    for i in e.topics:
      i = Bunch(i)
      for j in i.reports:
        j = Bunch(j)
        labels[j.usershowid] = ("report%s" % j.usershowid)
        alabels[j.usershowid] = ("abs%s" %j.usershowid)
	    # npuauthornew( uid, name, num, tituly)
      if flag == 0:
        authors = [ npuauthor(labels[j["usershowid"]], j["name"], getindex(j)) for j in i.reports] 
      else:
        authors = [ npuauthornew(labels[j["usershowid"]], j["name"], j["usershowid"], gettituly(j), getindex(j)) for j in i.reports] 
      piyo = [ j["time"] for j in i.reports ]
      ret = specialtable_inner(authors, piyo)
      attr = gethostsattr(i)
      hoge = ", ".join([idx_name(k["name"], getindex(k)) for k in getattr(i, attr)])
      print("\specialtalk{%s}{%s}{%s}{%s}{\\cn%s}{%s}%%" % (i.topic_name, i.room, hoge, ret, attr, i.topic_name.split(" ")[0]))


def longlist( sess ):
  global labels, alabels
  for e in sess:
    print("\section{%s}"% e.session_name)
    for i in e.topics:
      i = Bunch(i)
      print("\\begin{figure}[H]{\\nputopic{%s}%%" % i.topic_name)
      print(nputime(e.date, i.room) + "%%")
      print(npuleaderlist(i) + "%%")

      print("\\subsectocont{\qquad\quad %s}\\npureportlist{%%"% i.topic_name)
      hoge = []
      for j in i.reports:
        j = Bunch(j)
        lj = labels[j.usershowid]
        alj = alabels[j.usershowid]
        hoge.append(npureport(nputitle(j.title, alj), lj, j.name, j.school, j.time, j.index if hasattr(j, "index") else j.name))
      print("\t" + "%%\n\t".join(hoge) + "}}\\end{figure}\\pagebreak[0]\\vskip25pt%%")


def abstlist( sess ):
  global alabels
  for e in sess:
    print("\section{%s}"% e.session_name)
    for i in e.topics:
      i = Bunch(i)
      print("\subsection{%s}"% i.topic_name)
      for j in i.reports:
        j = Bunch(j)
        lj = alabels[j.usershowid]
        # hoge = npufootauthor(j.author, j.name, j.school, j.email.replace("_", "\\_") if hasattr(j, 'email') else "")
        tmp1 = npufootstart(j.author if hasattr(j, "author") else j.name, j.name, j.index if hasattr(j, "index") else j.name)
        tmp2 = npufootend(j.name, j.school, j.email.replace("_", "\\_") if hasattr(j, 'email') else "")
        print(npuabstractnew(j.title, lj, tmp1, j.abstract, tmp2))
        # print(npuabstract(j.title, lj, hoge, j.abstract))

def outputall( sess ):
  ret = []
  for e in sess:
    for i in e.topics:
      for j in i["reports"]:
        j["usershowid"] = int(j["usershowid"])
      ret.extend(i["reports"])

  ret.sort(key=lambda obj:obj.get('usershowid', 40000), reverse=False)
  for j in ret:
    print("%s,%s,%s"% (j["usershowid"], j["name"], j["school"]))

def sortsess(sess):
  j = 0
  name = [ "One", "Two", "Three", "Four", "Five", "Six"]
  for e in sess:
    e.topics.sort()
    topics = ["\\hyperlink{" +i.split(",")[0] +"}{"+i.split(",")[0] +"}"  for i in e.topics]
    print("\\def\\s"+ name[j] + "{" +" ".join(topics) + "}")
    j += 1
  return sess


def main():
  global flag
  session = json.load(open("session.json", 'r'))
  topic = json.load(open("topic.json", "r"))
  report = json.load(open("report_list.json", 'r'))

  sysold = sys.stdout

  sess = [Bunch(_) for _ in session]
  with open("auto_session.tex", "w") as f:
    sys.stdout = f 
    sess = sortsess(sess)
    sys.stdout = sysold

  sess = ppreprocess(sess, topic)
  sess = presort( sess, report )

  
  # flag = len(sys.argv) > 1
  # print("AAAA %d"% flag)
  with open("auto_list_short.tex", "w") as f:
    sys.stdout = f
    shortlist(sess)
    sys.stdout = sysold

  with open("auto_list_long.tex", "w") as f:
    sys.stdout = f
    longlist(sess)
    sys.stdout = sysold

  with open("auto_list_abst.tex", "w") as f:
    sys.stdout = f
    abstlist(sess)
    sys.stdout = sysold

  # with open("auto_all_reports.csv", "w") as f:
  #   sys.stdout = f
  #   outputall(sess)
  #   sys.stdout = sysold

if __name__ == '__main__':
  main()
