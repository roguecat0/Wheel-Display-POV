package com.example.imagesendapp

import android.graphics.Bitmap
import android.util.Log
import com.example.imagesendapp.Constants.LEDS
import com.example.imagesendapp.Constants.SLICES
import com.example.imagesendapp.ImageTransformer.bmp
import com.example.imagesendapp.ui.theme.cols
import org.opencv.android.Utils
import org.opencv.core.*
import org.opencv.imgproc.Imgproc
import java.io.File
import java.util.*
import kotlin.math.pow

// object om de Transformatie data van de app constant te houden doorheen de app
object ImageTransformer {
    private var mat = Mat();
    private var prevMat = Mat();
    var conf = Bitmap.Config.ARGB_8888 // see other conf types
    var bmp = Bitmap.createBitmap(10, 10, conf)
    // converteert bitmap foto naar opencv Mat()
    fun setImage(bitmap: Bitmap){
        this.bmp = bitmap.copy(Bitmap.Config.ARGB_8888, true)
        Utils.bitmapToMat(bmp,mat);
        mat.copyTo(prevMat)
    }
    // converteert foto naar van x,y naar polaire coordinaten
    fun toPolar(reset: Boolean = false){
        if (reset) resetMat();
        val img = Mat()
        mat.convertTo(img, CvType.CV_32F)
        val polar = Mat()
        val length = maxOf(img.rows(), img.cols()) / 2.0
        val center = Point(img.cols() / 2.0, img.rows() / 2.0)

        Imgproc.linearPolar(
            img,
            polar,
            center,
            length,
            Imgproc.WARP_FILL_OUTLIERS
        )
        polar.convertTo(mat, CvType.CV_8U)
    }
    // veranderd de resolutie naar die met de juiste hoeveelheid leds en SLICES
    fun changeResolution(ampitude: Int = LEDS, angular: Int = SLICES, reset: Boolean = false){
        if (reset) resetMat();
        val img = Mat()
        val newDim = Size(ampitude.toDouble(), angular.toDouble())

        Imgproc.resize(mat, img, newDim, 0.0, 0.0, Imgproc.INTER_AREA)

        if (!img.empty()){
            img.copyTo(mat)
        }
    }
    // polar en resize te samen
    fun encodeImage(reset: Boolean = false){
        if (reset) resetMat();
        toPolar();
        changeResolution();
    }
    // verander de de foto naar een form die makkelijker word uitgelezen door de esp
    fun toEspRegister(): List<List<Int>> {
        val image = Mat()
        Imgproc.cvtColor(mat,image,Imgproc.COLOR_RGB2BGR)
        val serial = 7
        assert(image.cols() % serial == 0) { "image shape ${image.size()} is not serializable with $serial" }
        val result = Array(image.rows()) { row ->
            Array(image.cols()) { col ->
                Array(3) {
                    toBitArray(image.get(row,col)[it].toInt())
                }.flatten().toTypedArray()
            }
        }

        val bitmap = mutableListOf<List<Int>>()
        val customArr = intArrayOf(12, 13, 14, 15, 16, 11, 10, 9, 8, 7, 6, 5, 4, 2)
        val arr = customArr.map { 2.0.pow(it).toInt() }.toTypedArray().reversedArray()
        Log.d("custom arr", arr.contentToString())
        for (row in result.withIndex()) {
            val registers = mutableListOf<Int>()

            for (s in 0 until serial) {

                assert(arr.size == image.cols() / serial) { "size of register index(${arr.size}) is not size of parallel LEDs(${image.cols() / serial})" }
                for (x in 0 until 24) {
                    val col = getColumn(row.value,x,s,serial)
                    if(row.index == 0 && s == 0){
                        if(x == 8 || x == 16) {Log.d("cols","break");}
                        Log.d("cols", "${col.contentToString()} (${row.index},$s,$x)")
                    }
                    registers.add(
                        dotProduct(col,arr)
                    )
                }
            }
            bitmap.add(registers.toList())
            Log.d("reg",registers.toString())
        }
        Log.d("esp", bitmap.toString())
        return bitmap.toList()
    }
    // converteerd de Mat terug naar een bitmap om het op het scherm te tonen
    fun getImage() : Bitmap{
        mat.convertTo(mat, CvType.CV_8U)
        bmp = Bitmap.createBitmap(mat.cols(), mat.rows(), conf)
        Utils.matToBitmap(mat,bmp);
        return bmp;
    }
    fun resetMat(){
        prevMat.copyTo(mat)
    }
}
// veranderd een getal naar een int array die zijn binaire waarde representeerd
fun toBitArray(number: Int) : Array<Int> {
    var x = Integer.toBinaryString(number)
    for(i in 0..(7-x.length))
        x = "0"+x
    return x.toCharArray().map {
        it.digitToInt() }.toTypedArray()
}
// haalt de een colom uit een 2 dimentionele Array<Int> met als stap groote x
fun getColumn(matrix: Array<Array<Int>>, columnIndex: Int, startingRow: Int, x: Int): Array<Int> {
    if (columnIndex >= 0 && columnIndex < matrix[0].size) {
        val column = mutableListOf<Int>()
        for (i in startingRow until matrix.size step x) {
            val row = matrix[i]
            if (columnIndex < row.size) {
                column.add(row[columnIndex])
            } else {
                throw IndexOutOfBoundsException("Invalid column index")
            }
        }
        return column.toTypedArray()
    } else {
        throw IndexOutOfBoundsException("Invalid column index")
    }
}
// berekend het inwendig product van 2 Array<Int>'s
fun dotProduct(arr1: Array<Int>, arr2: Array<Int>): Int {
    require(arr1.size == arr2.size) { "Arrays must have the same length" }

    var dotProduct = 0
    for (i in arr1.indices) {
        dotProduct += arr1[i] * arr2[i]
    }
    return dotProduct
}