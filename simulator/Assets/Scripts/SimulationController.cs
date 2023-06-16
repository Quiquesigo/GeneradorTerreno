using UnityEngine;
using UnityEngine.SceneManagement;

public class SimulationController : MonoBehaviour
{   private Camera activeCamera;
    private Camera mainCamera;
    private Camera cenitalCamera;
	private Camera littleCamera;

    void Start ()
	{
		mainCamera =GameObject.FindWithTag ("MainCamera").GetComponent<Camera>();
		mainCamera.GetComponent<AudioListener>().enabled = true;
		cenitalCamera = GameObject.Find("Cenital Camera").GetComponent<Camera>();
		cenitalCamera.GetComponent<AudioListener>().enabled = false;
		cenitalCamera.enabled = false;
		littleCamera = GameObject.Find("Little Camera").GetComponent<Camera>();
		littleCamera.GetComponent<AudioListener>().enabled = false;
		littleCamera.enabled = false;		


		activeCamera = mainCamera;

        Debug.Log ("Inicializacion control");
	}
    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.Escape))
            SceneManager.LoadScene("Menu");
            // Application.Quit();

        if (Input.GetKeyDown(KeyCode.M)) {
			activeCamera.enabled=false;
			activeCamera.GetComponent<AudioListener>().enabled = false;
			activeCamera = mainCamera;
			activeCamera.enabled=true;
			activeCamera.GetComponent<AudioListener>().enabled = true;

			Debug.Log ("Post cambio");
		}

		if (Input.GetKeyDown(KeyCode.C)) {
			activeCamera.enabled=false;
			activeCamera.GetComponent<AudioListener>().enabled = false;
			activeCamera = cenitalCamera;
			activeCamera.enabled=true;
			activeCamera.GetComponent<AudioListener>().enabled = true;
			Debug.Log ("C cambio");
		}

	   
		if (Input.GetKeyDown(KeyCode.L)) {
			if (littleCamera.enabled){
				littleCamera.enabled=false;
			}
			else{
				littleCamera.enabled=true;
				Debug.Log ("L cambio");
			}
		}
	}

        
    
}
