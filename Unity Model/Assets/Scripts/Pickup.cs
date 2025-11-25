using UnityEngine;
using System.Collections.Generic;

public class RobotCargador : MonoBehaviour
{
    public Transform carryPoint;      // Empty donde se apilan las cajas
    public float alturaCaja = 0.5f;   // La altura de cada caja (ajusta según tu modelo)
    public int maxCajas = 5;

    private List<GameObject> cajasCargadas = new List<GameObject>();

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Box"))
        {
            // NO recoger si ya tiene 5 cajas
            if (cajasCargadas.Count >= maxCajas)
                return;

            TomarCaja(other.gameObject);
        }
    }

    private void TomarCaja(GameObject caja)
    {
        // Desactivar física
        Rigidbody rb = caja.GetComponent<Rigidbody>();
        if (rb != null) rb.isKinematic = true;

        // Hacer la caja hija del carryPoint
        caja.transform.SetParent(carryPoint);

        // Calcular altura donde va esta caja
        float nuevaAltura = alturaCaja * cajasCargadas.Count;

        // Posicionar justo encima de las demás
        caja.transform.localPosition = new Vector3(0, nuevaAltura, 0);
        caja.transform.localRotation = Quaternion.identity;

        // Guardarla en la lista
        cajasCargadas.Add(caja);
    }
}
