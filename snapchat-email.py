from argparse import ArgumentParser
from snapchat_bots import SnapchatBot
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

class EmailBot(SnapchatBot):
    def __init__(self, username, password, smtp, emailuser, emailpass, sender, recipient):
        SnapchatBot.__init__(self, username, password)
        self.smtp = smtp or "smtp.gmail.com:587"
        self.emailuser = emailuser
        self.emailpass = emailpass
        self.sender = sender or self.emailuser
        # by default, send to yourself
        self.recipient = recipient or self.sender

    def on_snap(self, snapsender, snap):
        # check media type. currently only supports photos.
        # todo: magic number!
        if snap.media_type != 0:
            # not an image. abort.
            print("Ignoring non-image snap.")
            return

        # Construct email message with image attached
        msg = MIMEMultipart()
        msg['Subject'] = 'Snap from ' + snapsender
        msg['From'] = 'SnapchatEmail Bot'
        msg['To'] = self.recipient
        with open(snap.file.name, 'rb') as fp:
            img = MIMEImage(fp.read())
            msg.attach(img)

        # Connect to SMTP server and send message
        s = smtplib.SMTP(self.smtp)
        s.ehlo()
        s.starttls()
        s.login(self.emailuser, self.emailpass)
        s.sendmail(self.sender, ", ".join([self.recipient]), msg.as_string())
        s.quit()

        print("Emailed snap from " + snapsender + ".")

    def on_friend_add(self, friend):
        """ Add anyone who adds me """
        self.add_friend(friend)

    def on_friend_delete(self, friend):
        """ Delete anyone who deletes me """
        self.delete_friend(friend)

if __name__ == '__main__':
    parser = ArgumentParser("Email Bot")
    parser.add_argument(
            '-u', '--username', required=True, type=str,
            help="Snapchat username to run the bot on")
    parser.add_argument(
            '-p', '--password', required=True, type=str,
            help="Snapchat password")
    parser.add_argument(
            '-s', '--smtp', required=False, type=str,
            help="Address of the SMTP server to send email from")
    parser.add_argument(
            '-eu', '--emailuser', required=True, type=str,
            help="SMTP username")
    parser.add_argument(
            '-ep', '--emailpass', required=True, type=str,
            help="SMTP password")
    parser.add_argument(
            '-f', '--sender', required=False, type=str,
            help="Sender email address")
    parser.add_argument(
            '-t', '--recipient', required=False, type=str,
            help="Recipient email address")

    args = parser.parse_args()

    bot = EmailBot(args.username, args.password, args.smtp, args.emailuser, args.emailpass, args.sender, args.recipient)
    bot.listen(timeout=5)
