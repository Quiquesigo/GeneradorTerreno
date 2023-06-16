/*
using Matrix;
using Matrix.Extensions.Client.Message;
using Matrix.Xmpp.Client;
using Matrix.Xmpp.XData;
*/
using S22.Xmpp;
using S22.Xmpp.Client;
using System.Collections;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Globalization;
using System.Threading.Tasks;
using TMPro;
using UnityEngine;
using UnityEngine.AI;

public class Entity : MonoBehaviour
{
    [SerializeField] TextMeshPro text;
    [SerializeField] GameObject coloredPart;
    [SerializeField] float distanceTargetThreshold = 0.5f;
    [SerializeField] float stuckSecondsThreshold = 1f;
    [SerializeField] float stuckDistanceThreshold = 0.2f;

    private CameraManager camManager;
    private NavMeshAgent navMeshAgent;
    private TcpImageManager tcpImageManager;
    private XmppClient xmppClient;
    // private TcpCommandManager tcpCommandManager;
    private Vector3 stuckPosition;
    private bool goalSet;
    private bool agentCollision;
    private float stuckTimer;

    private int conexionNumber;

    private float radioCom=24;
    private Dictionary<string, GameObject> entities;
    private Dictionary<string, GameObject> comBeams;
   

    private void Awake() {
        camManager = GetComponent<CameraManager>();
    }

    private void Start() {
        goalSet = false;
        text.text = name;
        stuckTimer = 0;
        stuckPosition = transform.position;
        navMeshAgent = GetComponent<NavMeshAgent>();
        SetObstacleAvoidance(agentCollision);
        //conexionNumber=0;
        comBeams = new Dictionary<string, GameObject>();
    }

    private void Update() {
        // TakePictureOnMouseClick();
        // GoToPointOnMouseClick();
        CheckNeighbors();
        CheckIfGoalAchieved();
        if (goalSet)
            CheckIfStuck();
    }


    public void SetTargetPosition(Vector3 point) {
        navMeshAgent.destination = point;
        goalSet = true;
    }

    private void CheckIfGoalAchieved() {
        if (goalSet && navMeshAgent.remainingDistance <= distanceTargetThreshold) {
            if (Vector3.SqrMagnitude(navMeshAgent.destination - transform.position) <= distanceTargetThreshold) {
                goalSet = false;
                SendPosition(navMeshAgent.destination);
            }
        }
    }

    private void CheckIfStuck() {
        stuckTimer += Time.deltaTime;
        if (stuckTimer > stuckSecondsThreshold) {
            if (Vector3.Distance(transform.position, stuckPosition) < stuckDistanceThreshold) {
                goalSet = false;
                navMeshAgent.destination = transform.position;
                SendPosition(transform.position);
                // var task = SendPositionAsync(transform.position);
                //task.Wait();
            }
            stuckTimer = 0;
            stuckPosition = transform.position;
        }
    }

    public void ChangeColor(Color color) {
        coloredPart.GetComponent<Renderer>().material.color = color;
    }
    public void CameraFov(int cameraIndex, float fov) {
        if (camManager != null)
            camManager.CameraFov(cameraIndex, fov);
    }

    public void CameraMove(int cameraIndex, Vector3 axis, float units) {
        if (camManager != null)
            camManager.CameraMove(cameraIndex, axis, units);
    }

    public void CameraRotate(int cameraIndex, Vector3 axis, float degrees) {
        if (camManager != null) {
            var rotation = new Vector3(
                (degrees - transform.rotation.x) * axis.x, 
                (degrees - transform.rotation.y) * axis.y, 
                (degrees - transform.rotation.z) * axis.z
            );
            camManager.CameraRotate(cameraIndex, rotation);
        }
    }

    private void GoToPointOnMouseClick(int button = 1) {
        if (Input.GetMouseButtonDown(button)) {
            var ray = Camera.main.ScreenPointToRay(Input.mousePosition);
            if (Physics.Raycast(ray, out RaycastHit hit)) {
                Debug.Log("Go to: " + hit.point);
                SetTargetPosition(hit.point);
            }
        }
    }

    public void SendCurrentPosition() {
        SendPosition(transform.position);
    }

	public void SendPosition(Vector3 point) {
        // string position = Utils.Vector3ToPosition(point);
        string position = JsonUtility.ToJson(point);
        string name = this.name;
        // var task = Task.Run(async () => await XmppCommunicator.SendXmppCommand(xmppClient, name, xmppClient.XmppDomain, position));
        // task.Wait();
        XmppCommunicator.SendXmppCommand(xmppClient, position, new Jid(xmppClient.Jid.Domain, name));
        //Debug.Log(position);
        // tcpCommandManager.SendMessageToClient(position);
    }


    private void SetObstacleAvoidance(bool agentCollision) {
        if (navMeshAgent != null) {
            if (agentCollision)
                navMeshAgent.obstacleAvoidanceType = ObstacleAvoidanceType.HighQualityObstacleAvoidance;
            else
                navMeshAgent.obstacleAvoidanceType = ObstacleAvoidanceType.NoObstacleAvoidance;
        }
    }

    public void LaunchTakePicture(int cameraIndex, float captureFrequency) {
        if (camManager != null) {
            camManager.SetFrequency(cameraIndex, captureFrequency);
            camManager.LaunchTakePicture(cameraIndex);
        }
    }

    public void StartListeningImages() {
        camManager.XmppClient = xmppClient;
        // camManager.ImageQueue = tcpImageManager.StartListeningImages();
    }

    public void CheckNeighbors(){
        //private Dictionary<string, LineRenderer> comBeams;
        int counter=-1;
        //comBeams = new Dictionary<string, GameObject>();
        entities = GameObject.Find("Agent Manager").GetComponent<XmppCommunicationManager>().Entities;
       
        Debug.Log("Dist "+this.name);
       // bool itself=false;
        foreach(var element in entities){
            /*if (itself)
                counter++;
            else if(element.Value.name==this.name)
                    itself=true;*/
            float dist=Vector3.Distance(element.Value.transform.position,transform.position);
            if (comBeams.ContainsKey(element.Value.name)){
                    Debug.Log("repe");
                    Destroy(comBeams[element.Value.name]);
                }
            if ((dist <= radioCom)&&(element.Value.name!=this.name)){
                LineRenderer newBeam;
                counter++;
                Debug.Log("Dist 0"+element.Value.name);
                //var LineRendered miLinea=GetComponent<LineRendered>;
                
                comBeams[element.Value.name]=new GameObject();
                comBeams[element.Value.name].AddComponent<LineRenderer>(); 
                Debug.Log("Dist 1 "+element.Value.name+" "+comBeams[element.Value.name]);
                newBeam=comBeams[element.Value.name].GetComponent<LineRenderer>();
                
                newBeam.SetPosition(0, element.Value.transform.position);
                Debug.Log("Dist 2 "+ element.Value.transform.position);
                newBeam.SetPosition(1,transform.position); 
                Debug.Log("Dist 3 "+ transform.position); 
            }
        }   
        Debug.Log("Vecinos "+this.name+ " "+counter);
    }

    public TcpImageManager TcpImageManager {
        get { return tcpImageManager; }
        set { tcpImageManager = value; }
    }

    /*
    public TcpCommandManager TcpCommandManager {
        get { return tcpCommandManager; }
        set { tcpCommandManager = value; }
    }
    */

    public XmppClient XmppClient {
        get { return xmppClient; }
        set { 
            xmppClient = value; 
            camManager.XmppClient = xmppClient;
        }
    }

    public NavMeshAgent NavMeshAgent {
        get { return navMeshAgent; }
    }

    public bool AgentCollision {
        get { return agentCollision; }
        set { agentCollision = value; }
    }
}
