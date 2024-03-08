package assignment1

/**
 * Created by Tan Dang on 22/02/2024
 */

import java.nio.charset.{Charset, StandardCharsets}
import java.nio.file.{Files, Paths}
import scala.collection.mutable
import scala.io.Source
import scala.jdk.CollectionConverters.*

val FOLDER_PATH = "reuters/test"

@main
def main(): Unit = {
  try {
    // generate a map of docID to tokens
    var mapDocIdToTokens = Map[String, Set[String]]()
    val files = getFilesInFolder(FOLDER_PATH)
    files.foreach(filePath => {
      val docID = filePath.substring(13)
      readFile(filePath) match {
        case Some(content) =>
          val setUniqueWords = tokenize(content)
          mapDocIdToTokens += (docID -> setUniqueWords)
        case None =>
          println(s"Failed to read file: $filePath")
      }
    })
//    mapDocIdToTokens.foreach((k, v) => println(s"DocID: $k, Tokens: $v"))

    // generate a map of tokens to docID
    val mapTokenToDocIds = mutable.TreeMap[String, mutable.TreeSet[String]]()
    mapDocIdToTokens.foreach((docID, tokens) => {
      tokens.foreach(token => {
        if (mapTokenToDocIds.contains(token)) {
          val setDocId = mapTokenToDocIds(token)
          mapTokenToDocIds += (token -> setDocId.union(Set(docID)))
        } else {
          mapTokenToDocIds += (token -> mutable.TreeSet(docID))
        }
      })
    })
//    mapTokenToDocIds.foreach((k, v) => println(s"Token: $k, DocIDs: $v"))
//    writeFile("index.txt", generateContentToWrite(mapTokenToDocIds))
  } catch {
    case e: Throwable => println(e)
  }
}

def generateContentToWrite(mapTokenToDocIds: mutable.TreeMap[String, mutable.TreeSet[String]]): String = {
  val sb = new StringBuilder
  mapTokenToDocIds.foreach((token, docIds) => {
    sb.append(token + "\t")
    docIds.foreach(docId => sb.append(docId + " "))
    sb.append("\n")
  })
  sb.toString()
}

def writeFile(filePath: String, content: String): Unit = {
  val path = Paths.get(filePath)
  Files.write(path, content.getBytes)
}

def getFilesInFolder(folderPath: String): Set[String] = {
  val path = Paths.get(folderPath)
  val files = Files.list(path)
  try {
    files.iterator().asScala.map(_.toString).toSet
  } finally {
    files.close()
  }
}

def readFile(filePath: String): Option[String] = {
  val charset: Charset = StandardCharsets.ISO_8859_1 // add this to read European characters in file 17980
  val source = Source.fromFile(filePath)(charset)
  try {
    Some(source.mkString)
  } catch {
    case e: Exception =>
      println(e)
      None
  } finally {
    source.close()
  }
}

def tokenize(content: String): Set[String] = {
  content.toLowerCase().split("[\\s\\p{Punct}]+").toSet
}