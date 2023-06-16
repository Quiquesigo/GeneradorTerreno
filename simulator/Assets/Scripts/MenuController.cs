using System;
using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class MenuController : MonoBehaviour
{
    public TMP_InputField xmppNode;
    public TMP_InputField xmppDomain;
    public TMP_InputField xmppPass;
    public TMP_InputField xmppPort;
    public Toggle xmppTls;
    public TMP_InputField ipAddress;
    public TMP_InputField commandPort;
    public TMP_InputField imagePort;
    public TMP_Dropdown resolution;
    public Toggle fullscreen;
    Resolution[] resolutions;

    [SerializeField] private Button save;

    private Color normalColorText;
    private Color errorColorText;
    private Color saveColorBg;

    /*
    private string[] ipAddress;
    private int[] commandPort;
    private int[] imagePort;
    private int[] resolutionIndex;
    private bool[] fullscreen;

    private const int CURRENT = 0;
    private const int MODIFIED = 1;

    void Awake() {
        ipAddress = new string[2];
        commandPort = new int[2];
        imagePort = new int[2];
        resolutionIndex = new int[2];
        fullscreen = new bool[2];
        PopulateFromPlayerPrefs();
    }
    */

    private void Awake() {
        errorColorText = Color.red;
        normalColorText = commandPort.colors.selectedColor;
        saveColorBg = save.image.color;
    }

    private void Start() {
        resolutions = Screen.resolutions;
        PopulateResolutionDropdown();
        PopulateFromPlayerPrefs();
    }

    private void Update() {
        bool errors = false;
        errors |= CheckPortText(xmppPort);
        UpdateSaveButton(errors);
    }

    private void UpdateSaveButton(bool errors) {
        save.enabled = !errors;
        if (errors)
            save.image.color = Color.gray;
        else
            save.image.color = saveColorBg;
    }

    private bool CheckPortText(TMP_InputField control) {
        bool error = false;
        if (!AllNumbers(control.text))
            error = true;
        else {
            var value = int.Parse(control.text);
            if (value < 1 || value > 65535)
                error = true;
        } 
        ChangeColorOnError(control, error);
        return error;
    }

    private void ChangeColorOnError(TMP_InputField control, bool error) {
        var colors = control.colors;
        if (error) {
            colors.selectedColor = errorColorText;
            colors.normalColor = errorColorText;
        } else {
            colors.selectedColor = normalColorText;
            colors.normalColor = normalColorText;
        }
        control.colors = colors;
    }

    private bool AllNumbers(string text) {
        bool result = true;
        for (int i = 0; i < text.Length && result; i++)
            result &= char.IsDigit(text[i]);
        return result;
    }

    private void PopulateResolutionDropdown() {
        resolution.ClearOptions();
        int currentResolutionIndex = 0;
        List<string> resolutionDescriptions = new List<string>();
        for (int i = 0; i < resolutions.Length; i++) {
            string resolution = resolutions[i].width + " x " + resolutions[i].height;
            resolutionDescriptions.Add(resolution);
            if (IsActiveResolution(resolutions[i]))
                currentResolutionIndex = i;
        }
        resolution.AddOptions(resolutionDescriptions);
        resolution.value = currentResolutionIndex;
        resolution.RefreshShownValue();
    }

    private bool IsActiveResolution(Resolution resolution) {
        Resolution current = Screen.currentResolution;
        return resolution.width == current.width && resolution.height == current.height;
    }

    public void PopulateFromPlayerPrefs() {
        if (PlayerPrefs.HasKey("xmppNode"))
            xmppNode.text = PlayerPrefs.GetString("xmppNode");
        if (PlayerPrefs.HasKey("xmppDomain"))
            xmppDomain.text = PlayerPrefs.GetString("xmppDomain");
        if (PlayerPrefs.HasKey("xmppPass"))
            xmppPass.text = PlayerPrefs.GetString("xmppPass");
        if (PlayerPrefs.HasKey("xmppPort"))
            xmppPort.text = PlayerPrefs.GetInt("xmppPort").ToString();
        if (PlayerPrefs.HasKey("xmppTls"))
            xmppTls.isOn = Convert.ToBoolean(PlayerPrefs.GetInt("xmppTls"));
        if (PlayerPrefs.HasKey("resolution"))
            resolution.value = PlayerPrefs.GetInt("resolution");
        if (PlayerPrefs.HasKey("fullscreen"))
            fullscreen.isOn = Convert.ToBoolean(PlayerPrefs.GetInt("fullscreen"));
    }

    public void SavePlayerPrefs() {
        PlayerPrefs.SetString("xmppNode", xmppNode.text);
        PlayerPrefs.SetString("xmppDomain", xmppDomain.text);
        PlayerPrefs.SetString("xmppPass", xmppPass.text);
        PlayerPrefs.SetInt("xmppPort", int.Parse(xmppPort.text));
        PlayerPrefs.SetInt("xmppTls", Convert.ToInt32(xmppTls.isOn));
        PlayerPrefs.SetInt("resolution", resolution.value);
        PlayerPrefs.SetInt("fullscreen", Convert.ToInt32(fullscreen.isOn));
        PlayerPrefs.Save();
    }

    public void SetResolution(int resolutionIndex) {
        if (resolutionIndex >= resolutions.Length)
            resolutionIndex = resolutions.Length - 1;
        Resolution resolution = resolutions[resolutionIndex];
        Screen.SetResolution(resolution.width, resolution.height, Screen.fullScreen);
    }

    public void QuitApplication() {
        Application.Quit();
    }

    public void SetFullscreen(bool fullscreen) {
        Screen.fullScreen = fullscreen;
    }

    public void StartSimulator() {
        SceneManager.LoadScene("SandBox");

    }
}
