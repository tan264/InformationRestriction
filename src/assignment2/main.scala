package assignment2

/**
 * Created by Tan Dang on 07/03/2024
 */

import java.nio.charset.{Charset, StandardCharsets}
import scala.collection.immutable.{ListMap, ListSet}
import scala.io.Source

val INDEX_PATH = "index.txt"

@main
def main(): Unit = {
  val index = loadIndex(INDEX_PATH)
  //  val index = ListMap("the" -> ListSet("1", "2", "3"), "bond" -> ListSet("2", "3", "4"))
  index match {
    case Some(value) =>
      val searchResult = searchQuery("threat AND (NOT threaten)", value)
      searchResult match {
        case Some(value) =>
          value.foreach(docID => print(docID + " "))
        case None => println("Invalid query")
      }

    case None => println("Failed to load index")
  }
}

def searchQuery(query: String, index: ListMap[String, ListSet[String]]): Option[ListSet[String]] = {
  val tokens = query.split(" ")
  if (tokens.contains("AND") && tokens.length == 3) {
    val token1 = tokens(0)
    val token2 = tokens(2)
    return Some(searchAnd(token1, token2, index))
  } else if (tokens.contains("OR") && tokens.length == 3) {
    val token1 = tokens(0)
    val token2 = tokens(2)
    return Some(searchOr(token1, token2, index))
  } else if (tokens.contains("AND") && tokens.length == 4) {
    val token1 = tokens(0)
    val token2 = tokens(3).substring(0, tokens(3).length - 1)
    return Some(searchAndNot(token1, token2, index))
  } else if (tokens.contains("OR") && tokens.length == 4) {
    val token1 = tokens(0)
    val token2 = tokens(3).substring(0, tokens(3).length - 1)
    return Some(searchOrNot(token1, token2, index))
  }
  None
}

def search(token: String, index: ListMap[String, ListSet[String]]): ListSet[String] = {
  index.getOrElse(token, ListSet())
}

def searchAnd(token1: String, token2: String, index: ListMap[String, ListSet[String]]): ListSet[String] = {
  val result1 = search(token1, index)
  val result2 = search(token2, index)
  result1.intersect(result2)
}

def searchOr(token1: String, token2: String, index: ListMap[String, ListSet[String]]): ListSet[String] = {
  val result1 = search(token1, index)
  val result2 = search(token2, index)
  result1.union(result2)
}

def searchNot(token: String, index: ListMap[String, ListSet[String]]): ListSet[String] = {
  val allFiles = index.values.flatten.to(ListSet)
  val result = search(token, index)
  allFiles.diff(result)
}

def searchAndNot(token1: String, token2: String, index: ListMap[String, ListSet[String]]): ListSet[String] = {
  val result1 = search(token1, index)
  val result2 = searchNot(token2, index)
  result1.intersect(result2)
}

def searchOrNot(token1: String, token2: String, index: ListMap[String, ListSet[String]]): ListSet[String] = {
  val result1 = search(token1, index)
  val result2 = searchNot(token2, index)
  result1.union(result2)
}

def loadIndex(indexPath: String): Option[ListMap[String, ListSet[String]]] = {
  val charset: Charset = StandardCharsets.ISO_8859_1 // add this to read European characters in file 17980
  val source = Source.fromFile(indexPath)(charset)
  try {
    val lines = source.getLines()
    Some(lines.map(line => {
      val parts = line.split("\t")
      val word = parts(0)
      val files = parts(1).split(" ").to(ListSet)
      (word, files)
    }).to(ListMap))
  } catch {
    case e: Exception =>
      println(e)
      None
  } finally {
    source.close()
  }
}
