val fTxt =  file("/home/hhrutz/Documents/gmpu/lehre/sose2025/wf-mm-ar-SoSe-2025/materials-1/Lim2021_WhyArtisticResearchMattersBeyondTheEcoLogicalAndTowardsTheEcoSensitive-Writing.txt")
require (fTxt.exists())
val fSRT = fTxt.replaceExt("srt")
require (!fSRT.exists())
val lines = io.Source.fromFile(fTxt).getLines.toSeq
val dos = new java.io.FileOutputStream(fSRT)
lines.zipWithIndex.foreach { case (ln, i) =>
  val start = ln.substring(1, 9)
  val stop  = ln.substring(12, 20)
  val text  = ln.substring(23).trim
  val s = (s"""${i + 1}
    |$start,000 --> $stop,000
    |$text
    |
    |""".stripMargin)
  dos.write(s.getBytes("UTF-8"))
  println(s)
}
dos.close()
