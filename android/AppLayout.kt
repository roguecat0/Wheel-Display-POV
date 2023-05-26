package com.example.imagesendapp.ui.theme

import android.graphics.Bitmap
import android.graphics.ImageDecoder
import android.net.Uri
import android.os.Build
import android.provider.MediaStore
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.example.imagesendapp.Constants
import com.example.imagesendapp.Constants.SLICES
import com.example.imagesendapp.ImageTransformer

// app homescreen
val reset = MutableList(SLICES) { MutableList(168) { 0 }.toList() }.toList()
@Composable
fun RequestContentPermission() {
    var imageUri by remember {
        mutableStateOf<Uri?>(null)
    }
    var prevUri by remember {
        mutableStateOf<Uri?>(null)
    }

    val context = LocalContext.current
    val bitmap =  remember {
        mutableStateOf<Bitmap?>(null)
    }
    val angle = remember {
        mutableStateOf(0f)
    }

    val launcher = rememberLauncherForActivityResult(contract =
    ActivityResultContracts.GetContent()) { uri: Uri? ->
        imageUri = uri
    }
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
    )
    {
        Spacer(modifier = Modifier.height(30.dp))
        Text(
            text = "POV Image Sender",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )
        Spacer(modifier = Modifier.height(30.dp))
        Column(
            modifier = Modifier.fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Bottom
        ) {
            // toond de foto als er 1 is ingeladen
            imageUri?.let {
//            Log.d("uri1","uri1: "+it.toString()+"uri2: "+prevUri?.toString())
                if (prevUri == it){
//                Log.d("uri","same uri")
                    bitmap.value = ImageTransformer.getImage()
                } else {
                    if (Build.VERSION.SDK_INT < 28) {
                        bitmap.value = MediaStore.Images
                            .Media.getBitmap(context.contentResolver,it)
                        bitmap.value?.let { btm ->
                            ImageTransformer.setImage(btm);
                        }
                    } else {
                        val source = ImageDecoder
                            .createSource(context.contentResolver,it)
                        bitmap.value = ImageDecoder.decodeBitmap(source)
                        bitmap.value?.let { btm ->
                            ImageTransformer.setImage(btm);
                        }
                    }
                    prevUri = it;
                }


                bitmap.value?.let {  btm ->
                    Image(bitmap = btm.asImageBitmap(),
                        contentDescription ="null",
                        modifier = Modifier.size(400.dp))
                }
            }
            Spacer(modifier = Modifier.height(30.dp))
            Row(){
                // knop om de foto uit de gallery te halen
                Button(onClick = {
                    launcher.launch("image/*")
                }) {
                    Text(text = "Pick image")
                }
                Spacer(modifier = Modifier.width(10.dp))
                // knop om de te transormeren en door te sturen
                Button(onClick = {
                    ImageTransformer.encodeImage();
                    sendData(
                        ImageTransformer
                            .toEspRegister()
                    )
                    Toast.makeText(context, "encode en getransformeert en verzonden", Toast.LENGTH_SHORT).show()
                    bitmap.value = ImageTransformer.getImage()
                }) {
                    Text(text = "send encoded")
                }
                Spacer(modifier = Modifier.width(10.dp))
                // knop om de hoek door te sturen
                Button(onClick = {
                    sendAngle(angle.value.toInt())
                    Toast.makeText(context, "hoek gestuurd", Toast.LENGTH_SHORT).show()
                    bitmap.value = ImageTransformer.getImage()
                }) {
                    Text(text = "send angle")
                }

            }
            Spacer(modifier = Modifier.height(40.dp))
            Row() {
                Spacer(modifier = Modifier.width(10.dp))
                Text(text = "angle: ${angle.value.toInt()}")
                Spacer(modifier = Modifier.width(10.dp))
                // bepaald de hoek de zal worden doorgestuurd
                Slider(
                    modifier = Modifier.fillMaxWidth(),
                    steps = SLICES,
                    valueRange = 0f..SLICES.toFloat(),
                    value = angle.value,
                    onValueChange = {
                        angle.value = it
                    },
                )
            }
        }

    }

}