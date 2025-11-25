using UnityEngine;

public class MovimientoRobot2 : MonoBehaviour
{
    public float speed = 5f;

    private int direccionIndex = 0;
    private bool detenido = false;

    private bool girando = false;
    public float anguloGiro = 90f;
    public float duracionGiro = 0.3f;

    void Update()
    {
        // Mover SOLO según la rotación actual
        if (!detenido && !girando)
        {
            transform.position += transform.forward * speed * Time.deltaTime;
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        // NO GIRAR si el trigger es un Robot
        if (other.CompareTag("Robot"))
        {
            StartCoroutine(DetenerYReanudar());
            return; 
        }

        // Gira si choca con shelf o paredes
        if (other.CompareTag("Shelf") || other.CompareTag("Wall"))
        {
            if (!girando)
                StartCoroutine(GirarSuave());
        }
    }

    private System.Collections.IEnumerator DetenerYReanudar()
    {
        detenido = true;
        yield return new WaitForSeconds(3f);
        detenido = false;
    }

    private System.Collections.IEnumerator GirarSuave()
    {
        girando = true;

        Quaternion rotInicial = transform.rotation;
        Quaternion rotFinal = rotInicial * Quaternion.Euler(0, anguloGiro, 0);

        float tiempo = 0f;

        while (tiempo < duracionGiro)
        {
            tiempo += Time.deltaTime;
            transform.rotation = Quaternion.Slerp(rotInicial, rotFinal, tiempo / duracionGiro);
            yield return null;
        }

        transform.rotation = rotFinal;
        girando = false;
    }
}
