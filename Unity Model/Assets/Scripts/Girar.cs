using UnityEngine;

public class GirarSoloSmooth : MonoBehaviour
{
    public float speed = 5f;
    public float anguloGiro = 90f;
    public float duracionGiro = 0.3f;
    private bool girando = false;

    void Update()
    {
        // Si no está girando, avanzar hacia adelante
        if (!girando)
        {
            transform.position += transform.forward * speed * Time.deltaTime;
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!girando && (other.CompareTag("Shelf") || other.CompareTag("Robot") || other.CompareTag("Wall")))
        {
            StartCoroutine(GirarSuave());
        }
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
