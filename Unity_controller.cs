using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public class ControllerSend : MonoBehaviour
{
    public OVRInput.Controller controller = OVRInput.Controller.RTouch;
    private UdpClient udp;
    private IPEndPoint endPoint;

    // 送信中フラグ
    private bool lastTriggerState = false;
    private bool lastAState = false;
    private bool lastBState = false;
    private Vector2 lastStick = Vector2.zero;
    



    void Start()
    {
        udp = new UdpClient();
        endPoint = new IPEndPoint(IPAddress.Parse("192.168.0.181"), 5005);

        // 送信を一定間隔コルーチンで行う
        StartCoroutine(SendLoop());
    }

    private System.Collections.IEnumerator SendLoop()
    {
        while (true)
        {
            yield return new WaitForSeconds(0.02f); // 20msごと（50Hz）

        //右トリガーの入力確認・状態送信

            // 右トリガー入力・判定（triggerは0〜1の範囲で動く）
            float trigger = OVRInput.Get(OVRInput.Axis1D.PrimaryIndexTrigger, controller);
            bool trigger_state = trigger > 0.5f;

            // 状態が変わった時だけ送信
            if (trigger_state != lastTriggerState)
            {
                lastTriggerState = trigger_state;

                string msg = trigger_state ? "Trigger_ON" : "Trigger_OFF";
                byte[] data = Encoding.UTF8.GetBytes(msg);
                udp.Send(data, data.Length, endPoint);
            }



        //Aボタンの入力確認・状態送信
           bool A_state = OVRInput.Get( OVRInput.Button.One, controller);

            if (A_state != lastAState)
            {

                lastAState = A_state;

                string msg = A_state ? "A_ON" : "A_OFF";
                byte[] data = Encoding.UTF8.GetBytes(msg);
                udp.Send(data, data.Length, endPoint);
            } 


        //Bボタンの入力確認・状態送信
            bool B_state = OVRInput.Get( OVRInput.Button.Two, controller);

            if (B_state != lastBState)
            {

                lastBState = B_state;

                string msg = B_state ? "B_ON" : "B_OFF";
                byte[] data = Encoding.UTF8.GetBytes(msg);
                udp.Send(data, data.Length, endPoint);
            } 

        // スティック入力（右コントローラ）
            Vector2 stick_state = OVRInput.Get(OVRInput.RawAxis2D.RThumbstick);

            // 微小な揺れを無視
            if (Vector2.Distance(stick_state, lastStick) > 0.1f)
            {
                lastStick = stick_state;

                // 関数名（メッセージ名）を既存と統一
                string msg = $"Stick:{stick_state.x:F2},{stick_state.y:F2}";
                byte[] data = Encoding.UTF8.GetBytes(msg);
                udp.Send(data, data.Length, endPoint);
            }
        
        }
    }
}