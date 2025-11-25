using UnityEngine;

public class MoverAlObjetivo : MonoBehaviour
{
    public float speed = 5f;
    public Transform objetivo;

    public bool activo = false;

    void Update()
    {
        if (!activo || objetivo == null) return;

        Vector3 direccion = (objetivo.position - transform.position).normalized;
        transform.position += direccion * speed * Time.deltaTime;
    }
}
