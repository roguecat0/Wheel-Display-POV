package com.example.imagesendapp.ui.theme

import android.util.Log
import com.example.imagesendapp.Constants.LEDS
import com.example.imagesendapp.Constants.SLICES
import org.java_websocket.WebSocket
import org.java_websocket.client.WebSocketClient
import org.java_websocket.handshake.ServerHandshake
import org.json.JSONObject
import java.net.URI

val cols = LEDS
val rows = SLICES
val dummyValues = MutableList(rows) { i -> MutableList(cols) { j -> (i * cols + j) }.toList() }.toList()
// stuurt data in de vorm van die de registers die de lijst kunnen door
fun sendData(bitmap: List<List<Int>> = dummyValues){
    val host = URI("ws://192.168.4.1/ws")
    // bij het openen van de connect word lijn per een lijst van de waardes doorgestuurd
    val client = object : WebSocketClient(host) {
        override fun onOpen(handshakedata: ServerHandshake?) {
            Log.d("COMS","handshake done")
            Log.d("COMS","bitmap: size: (${bitmap.size},${bitmap[0].size}) $bitmap")
            Log.d("COMS","dummyValues: size: (${dummyValues.size},${dummyValues[0].size}) $dummyValues")
            for ((k, v) in bitmap.withIndex()) {
                val jsonObject = JSONObject()
                jsonObject.put("$k", v)
                println(jsonObject.toString())
                send("{$k:$v}")
                println("{\"$k\":$v}")
                Thread.sleep(150)
            }
            close()
        }

        override fun onMessage(message: String?) {
            println(message)
        }

        override fun onClose(code: Int, reason: String?, remote: Boolean) {
            Log.d("COMS","closed")
            Log.d("COMS","remote: $remote")
            reason.let{
                Log.d("COMS","reason: $it")
            }

        }

        override fun onError(ex: Exception?) {
            Log.d("COMS", "error")
            ex?.printStackTrace()
        }
    }
    Log.d("COMS","connecting")
    client.connect()
    Log.d("COMS","finnished trying to connect")
}
// stuurt de hoek door waarmee de foto hoort te draaien
// word niet gebruikt
fun sendAngle(angle: Int){
    val host = URI("ws://192.168.4.1/ws")
    val client = object : WebSocketClient(host) {
        override fun onOpen(handshakedata: ServerHandshake?) {
            Log.d("COMS","{angle:$angle}")
            send("{angle:$angle}")
            Thread.sleep(150)
            close()
        }

        override fun onMessage(message: String?) {
            println(message)
        }

        override fun onClose(code: Int, reason: String?, remote: Boolean) {
            Log.d("COMS","closed")
            Log.d("COMS","remote: $remote")
            reason.let{
                Log.d("COMS","reason: $it")
            }
        }

        override fun onError(ex: Exception?) {
            Log.d("COMS", "error")
            ex?.printStackTrace()
        }
    }
    Log.d("COMS","connecting")
    client.connect()
    Log.d("COMS","finnished trying to connect")
}