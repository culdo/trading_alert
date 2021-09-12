from email_notification import send_mail
import os


def send_notify_email(line):
    content = line.notify_msg
    subject = f"TradingAlert {content}"
    filename = (subject + ".jpg").replace(" ", "_")
    line.plt_line.figure.savefig(filename)
    attach_plots = [filename]

    send_mail("wuorsut@gmail.com", subject,
              content)
    # os.remove(filename)
