using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class TemporizadorGlobal : MonoBehaviour
{
    public float tiempoLimite = 60f;
    private float tiempoActual = 0f;

    public TMP_Text textoTiempo;

    private bool juegoDetenido = false;

    void Update()
    {
        if (juegoDetenido) return;

        tiempoActual += Time.deltaTime;

        if (textoTiempo != null)
            textoTiempo.text = FormatearTiempo(tiempoActual);

        if (tiempoActual >= tiempoLimite)
        {
            DetenerTodo();
        }
    }

    private string FormatearTiempo(float t)
    {
        int minutos = Mathf.FloorToInt(t / 60);
        int segundos = Mathf.FloorToInt(t % 60);
        return minutos.ToString("00") + ":" + segundos.ToString("00");
    }

    private void DetenerTodo()
    {
        juegoDetenido = true;
        Time.timeScale = 0f;
        Debug.Log("Juego detenido por el temporizador.");
    }
}
