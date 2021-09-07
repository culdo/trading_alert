import winrt.windows.ui.notifications as notifications
import winrt.windows.data.xml.dom as dom


class Win10Toast:
    def __init__(self, content, title="Trading Alert"):
        app = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe'

        # create notifier
        nManager = notifications.ToastNotificationManager
        self.notifier = nManager.create_toast_notifier(app)

        # define your notification as string
        tString = """
          <toast>
            <visual>
              <binding template='ToastGeneric'>
                <text>Sample toast</text>
                <text>Sample content</text>
              </binding>
            </visual>
            <actions>
              <action
                content="Delete"
                arguments="action=delete"/>
              <action
                content="Dismiss"
                arguments="action=dismiss"/>
            </actions>        
          </toast>
        """
        tString = tString.replace("Sample toast", title)
        tString = tString.replace("Sample content", content)

        # convert notification to an XmlDocument
        self.xDoc = dom.XmlDocument()
        self.xDoc.load_xml(tString)

    def notify(self):
        # display notification
        self.notifier.show(notifications.ToastNotification(self.xDoc))
