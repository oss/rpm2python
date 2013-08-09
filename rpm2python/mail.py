import logging
import os

class MailHandler(logging.Handler):
    """This handler sends mail to us when there is a 500 error"""
    def __init__(self, sendmail, to, subject):
        logging.Handler.__init__(self)
        self.sendmail = sendmail
        self.to = to
        self.subject = subject

    def flush(self):
        #I'm not sure what this is for
        pass

    def emit(self, record):
    """Actually send the mail"""
        try:
            msg = self.format(record)
            p = os.popen("%s -t" % self.sendmail, 'w')
            p.write("To: %s\n" % self.to)
            p.write("Subject: %s\n" % self.subject)
            p.write(msg)
            p.close()
        except SystemExit:
            raise
        except:
            self.handleError(record)
