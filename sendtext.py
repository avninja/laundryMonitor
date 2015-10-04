import urllib
import urllib2
import smtplib

def sendText(number, subject, body):
    prov = ''
    url2 = 'http://www.txt2day.com/lookup.php'
    values2 = {'action' : 'lookup',
               'pre' : number[0:3],
               'ex' : number[3:6],
               'myButton' : 'Find Provider'}
    data2 = urllib.urlencode(values2)  ##provider checker
    req2 = urllib2.Request(url2, data2)
    response2 = urllib2.urlopen(req2)
    the_page2 = response2.read()
    if 'Telus' in the_page2:
        prov = 'msg.telus.com'
    if 'Bell' in the_page2:
        prov = 'txt.bellmobility.ca'
    if 'Rogers' in the_page2:
        prov = 'pcs.rogers.com'
    if 'Sprint' in the_page2:
        prov = 'messaging.sprintpcs.com'
    if 'Metropcs' in the_page2:
        prov = 'mymetropcs.com'
    if 'T-Mobile' in the_page2:
        prov = 'tmomail.net'
    if 'Verizon' in the_page2:
        prov = 'vtext.com'
    if 'Virgin Mobile' in the_page2:
        prov = 'vmobl.com'
    if 'AT&T' in the_page2:
        prov = 'txt.att.net'
    if prov == 0:
        print "Failed To Identify Provider\n"
        exit
    print prov
    smtpUser = 'avninjalaundry@gmail.com'
    smtpPass = '!abc123!'
    toAdd = number + "@" + prov
    fromAdd = smtpUser

    header = 'To:', toAdd + '\n' + 'From:', fromAdd + "\n" + 'Subject:', subject

    s = smtplib.SMTP('smtp.gmail.com',587)

    s.ehlo()
    s.starttls()
    s.ehlo()

    s.login(smtpUser, smtpPass)
    s.sendmail(fromAdd, toAdd, body)

    s.quit()

if __name__ == '__main__':
  sendText('6162592214', 'subject', 'bodyText')