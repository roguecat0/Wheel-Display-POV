import kotlinx.coroutines.runBlocking
import org.java_websocket.client.WebSocketClient
import org.java_websocket.handshake.ServerHandshake
import org.json.JSONObject
import org.json.JSONArray
import java.net.URI

fun main() = runBlocking {
    val dummyValues = listOf(
        listOf(
            1073741788, 1051446330, 401359398, 938989990, 1040732584, 348306368,
            930217074, 376933506, 1072679964, 918223842, 514938760, 524907458,
            921519638, 347970070, 881789072, 379954516, 1051446272, 401363840,
            938985496, 1046014558, 898040836, 509768788, 523200714, 937472326
        ),
        listOf(
            1073700828, 938472890, 439020966, 849797862, 940750128, 519846480,
            518825202, 394353178, 1072649628, 851374050, 392388288, 305797402,
            475548126, 1070021526, 899250952, 879382556, 938431872, 438979968,
            98502319
        )
    )

    //val dictVer = JSONArray(dummyValues.slice(0..2))
    val host = URI("ws://192.168.4.1/ws")
    val client = object : WebSocketClient(host) {
        override fun onOpen(handshakedata: ServerHandshake?) {
            for ((k, v) in dummyValues.withIndex()) {
                val jsonObject = JSONObject()
                jsonObject.put("$k", v)
                println(jsonObject)
                //send("{\"$k\":$v}")
                send(jsonObject.toString())
                println("{\"$k\":$v}")
                Thread.sleep(100)
            }
            close()
        }

        override fun onMessage(message: String?) {
            println(message)
        }

        override fun onClose(code: Int, reason: String?, remote: Boolean) {}

        override fun onError(ex: Exception?) {
            ex?.printStackTrace()
        }
    }
    client.connect()


}





