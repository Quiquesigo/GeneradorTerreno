/*
using Matrix;
using Matrix.Extensions.Client.Message;
using Matrix.Xmpp.Client;
using Matrix.Xmpp.XData;
using System.Threading.Tasks;
*/
using S22.Xmpp;
using S22.Xmpp.Client;
using S22.Xmpp.Im;
using UnityEngine;

/*
 * Low-level XMPP utility class.
 * Sends XMPP messages to XMPP server.
 */
public class XmppCommunicator
{
    public static void SendXmppCommand(XmppClient xmppClient, string content, Jid to, Jid from = null) {
        Message sendMessage = CreateMessage(xmppClient, content, to, from);
        xmppClient.SendMessage(AddCommandMetadata(ref sendMessage));
    }

    public static void SendXmppImage(XmppClient xmppClient, ImageData imageData, Jid to, Jid from = null) {
        string content = JsonUtility.ToJson(imageData);
        Message sendMessage = CreateMessage(xmppClient, content, to, from);
        xmppClient.SendMessage(AddImageMetadata(ref sendMessage));
    }

    private static Message CreateMessage(XmppClient xmppClient, string content, Jid to, Jid from = null) {
        Message message = new Message(to) {
            Body = content,
            Type = MessageType.Chat,
        };
        if (from != null)
            message.From = from;
        else
            message.From = xmppClient.Jid;
        return message;
    }

    private static Message AddCommandMetadata(ref Message message) {
        return AddTextSingleMetadata(ref message, "command");
    }
    private static Message AddImageMetadata(ref Message message) {
        return AddTextSingleMetadata(ref message, "image");
    }

    private static Message AddTextSingleMetadata(ref Message message, string metadata) {
        var x = message.Data.OwnerDocument.CreateElement("x", "jabber:x:data");
        x.SetAttribute("type", "form");
        var t = x.OwnerDocument.CreateElement("title");
        t.InnerText = "spade:x:metadata";
        var f = x.OwnerDocument.CreateElement("field");
        f.SetAttribute("var", "five");
        f.SetAttribute("type", "text-single");
        var v = f.OwnerDocument.CreateElement("value");
        v.InnerText = metadata;

        f.AppendChild(v);
        x.AppendChild(f);
        x.AppendChild(t);
        message.Data.AppendChild(x);

        return message;
    }
    /*
    public static async Task SendXmppCommand(XmppClient xmppClient, string username, string domain, string textMessage) {
        Jid jid = new Jid($"{username}@{domain}");
        await SendXmppCommand(xmppClient, jid, textMessage);
    }

    public static async Task SendXmppCommand(XmppClient xmppClient, Jid jid, string textMessage) {
        await SendMessageAsync(xmppClient, jid, textMessage, "command");
    }

    public static async Task SendXmppImage(XmppClient xmppClient, string username, string domain, ImageData imageData) {
        Jid jid = new Jid($"{username}@{domain}");
        await SendXmppImage(xmppClient, jid, imageData);
    }

    public static async Task SendXmppImage(XmppClient xmppClient, Jid jid, ImageData imageData) {
        string imageDataJson = JsonUtility.ToJson(imageData);
        await SendMessageAsync(xmppClient, jid, imageDataJson, "image");
    }

    private static async Task SendMessageAsync(XmppClient xmppClient, Jid jid, string textMessage, string fieldValue) {
        Message message = new Message(jid, textMessage) {
            XData = new Data(FormType.Form),
            Type = Matrix.Xmpp.MessageType.Chat
        };
        Field metadata = new Field("five", fieldValue) {
            Type = FieldType.TextSingle
        };
        message.XData.AddField(metadata);
        message.XData.Title = "spade:x:metadata";
        await xmppClient.SendMessageAsync(message);
    }
    */
}
