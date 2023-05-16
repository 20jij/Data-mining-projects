// THIS CODE IS MY OWN WORK, IT WAS WRITTEN WITHOUT CONSULTING
// A TUTOR OR CODE WRITTEN BY OTHER STUDENTS-Jason Ji

import java.io.File;
import java.io.FileNotFoundException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Scanner;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.zip.CRC32;
import java.nio.charset.StandardCharsets;
import java.util.Random;

public class minHash {

    //function that maps a 2D matrix coordinate into a 1D index.
    public static int getTriangleIndex(int i, int j, int numDocs){
        if (i == j) {
            System.err.println("Can't access triangle matrix with i == j");
            System.exit(1);
        }
        // make sure i < j
        if (j < i ) {
            int temp = i;
            i = j;
            j = temp;
        }
        // Calculate the index within the triangular array.
        int k = (int)(i * (numDocs - (i + 1) / 2.0) + j - i) - 1;
        return k;
    }

    // Generate a ArrayList of 'k' random coefficients for the random hash functions,
    // while ensuring that the same value does not appear multiple times in the list.
    public static ArrayList<Integer> pickRandomCoeffs(int k, int maxShingleID) {
        // Create a list of 'k' random values.
        ArrayList<Integer> randList = new ArrayList<Integer>();
        HashSet<Integer> usedSet = new HashSet<Integer>();
        Random random = new Random();
        while (k > 0){
            int randIndex = random.nextInt(maxShingleID + 1);

            // Ensure that each random number is unique.
            while (usedSet.contains(randIndex)) {
                randIndex = random.nextInt(maxShingleID + 1);
            }

            // Add the random number to the list and the set.
            randList.add(randIndex);
            usedSet.add(randIndex);
            k--;
        }
        return randList;
    }

    public static void runMinHash() {

        // number of components in the resulting MinHash signatures
        // it is also the number of random hash functions 
        int numHashes = 10;

        // specify the input dataset 
        int numDocs = 1000;

        String dataFile = "./data/articles_" + String.format("%d", numDocs) + ".train";
        String truthFile = "./data/articles_" + String.format("%d", numDocs) + ".truth";


        // convert documents to shingles
        System.out.println("Converting documents to shingles...");

        // Create a hashmap of the articles, mapping the article identifier (e.g., 
        // "t8470") to the list of shingle IDs that appear in the document.
        HashMap<String, HashSet<Integer>> docsAsShingleSets = new HashMap<String, HashSet<Integer>>();


        ArrayList<String> docNames = new ArrayList<>();

        long t0 = System.nanoTime();    

        int totalShingles = 0;

        // Open the data file.
        try {
            File myObj = new File(dataFile);
            Scanner myReader = new Scanner(myObj);
            for (int i = 0; i<numDocs; i++) {
                // Read all of the words (they are all on one line)
                String line = myReader.nextLine();
                line = line.replace("\n", "");
                ArrayList<String> words = new ArrayList<>(Arrays.asList(line.split(" ")));
                String docID = words.get(0);
                // Maintain a list of all document IDs.
                docNames.add(docID);

                words.remove(0);

                //'shinglesInDoc' will hold all of the unique shingle IDs present in the 
                //current document. 
                HashSet<Integer> shinglesInDoc = new HashSet<Integer>();
                
                // index starts with 1 to skip the first doc name
                for (int index = 0;index<words.size()-2;index++){
                    // 3 words shingle
                    String shingle = words.get(index) + " " + words.get(index+1) + " " + words.get(index + 2);
                    // Use CRC32 Hash to hash shingle to 32-bit integer
                    byte[] shingleBytes = shingle.getBytes(StandardCharsets.UTF_8);
                    CRC32 crc32 = new CRC32();
                    crc32.update(shingleBytes);
                    int crc = (int) (crc32.getValue() & 0xffffffffL); 
                    shinglesInDoc.add(crc);
                }

                // map docID to shingles 
                docsAsShingleSets.put(docID, shinglesInDoc);

                // count number  of total shinigles 
                totalShingles += (words.size()-2);

            } 
            myReader.close();
        } catch (FileNotFoundException e) {
            System.out.println("data file not found.");
        }

        long estimatedTime = System.nanoTime() - t0;
        double elapsedTimeInSecond = (double) estimatedTime / 1_000_000_000;

        System.out.println("Shingling " + String.format("%d", numDocs) + " docs took "+ Double.toString(
                elapsedTimeInSecond) + " sec.");
        double totalShingles_d = totalShingles;
        System.out.println(
                "Average shingles per doc: " + String.format("%f", totalShingles_d/numDocs));
               

        // Calculate Similarities
        int numElems = numDocs * (numDocs - 1) / 2;

        // 'JSim' will be for the actual Jaccard Similarity values. 
        //  'estJSim' will be for the estimated Jaccard Similarities found by comparing
        //  the MinHash signatures.
        double[] JSim = new double[numElems];
        double[] estJSim = new double[numElems];

        // Calculate Jaccard similarities, but only for small documents
        if (numDocs<=2500) {
            System.out.println("Calculating Jaccard Similarities... ");
            long t_jac = System.nanoTime();
            for (int i = 0; i < numDocs; i++ ) {
                if (i%100 == 0) {
                    System.out.println("  (" + Integer.toString(i) + " / " + Integer.toString (numDocs) + ")");
                } 
                HashSet<Integer> s1 = docsAsShingleSets.get(docNames.get(i));
                // Compare the doc witht the rest of the docs to compute Jacard similarities
                for (int j = i+1; j<numDocs; j++){
                    HashSet<Integer> s2 = docsAsShingleSets.get(docNames.get(j));
                    HashSet<Integer> intersection = new HashSet<Integer>(s1);
                    intersection.retainAll(s2);
                    HashSet<Integer> union = new HashSet<Integer>(s1);
                    union.addAll(s2);
                    double jacc_sim = (double)intersection.size() / (double)union.size();
                    JSim[getTriangleIndex(i, j,numDocs)] = jacc_sim;
                }  
            }
            long estimatedTime_jac = System.nanoTime() - t_jac;
            double elapsedTimeInSecond_jac = (double) estimatedTime_jac / 1_000_000_000;

            System.out.println("Calculating all Jaccard Similarities took " + Double.toString(
                    elapsedTimeInSecond_jac) + " sec.");
        }

        // delete JSim
        JSim = null;

        long t_minhash = System.nanoTime();

        // Generate Min Hash Signatures 
        System.out.println("Generating random hash functions...");

        int maxShingleID = (int)Math.pow(2,32) -1;
        long nextPrime = 4294967311L;

        // random hash function: h(x) = (a*x + b) % c
        // For each of the 'numHashes' hash functions, generate a different coefficient
        // 'a' and 'b'.
        ArrayList<Integer> coeffA = pickRandomCoeffs(numHashes,maxShingleID);
        ArrayList<Integer> coeffB = pickRandomCoeffs(numHashes, maxShingleID);

        System.out.println("Generating MinHash signatures for all documents...");

        ArrayList<ArrayList<Integer>> signatures = new ArrayList<ArrayList<Integer>>();
        
        // only generate random permutation of shingles exist in documents, and then take the lowest 
        // hash code (min hash), which represent the first shingle you would encounter randomly

        for (String docID : docNames) {
            HashSet<Integer> shingleIDSet = docsAsShingleSets.get(docID);
            ArrayList<Integer> signature = new ArrayList<Integer>();
            for (int i =0; i<numHashes; i++) {
                Integer minHashCode = (int)nextPrime+1;
                for (Integer shingleID: shingleIDSet) {
                    Integer hashCode = (int) ((coeffA.get(i) * shingleID + coeffB.get(i)) % nextPrime);
                    if (hashCode < minHashCode) {
                        minHashCode = hashCode;
                    }
                }
                signature.add(minHashCode);
            }
            signatures.add(signature);
        }

        long estimatedTime_minhash = System.nanoTime() - t_minhash;
        double elapsedTimeInSecond_minhash = (double) estimatedTime_minhash / 1_000_000_000;

        System.out.println("Generating MinHash signatures took " + Double.toString(
                elapsedTimeInSecond_minhash) + " sec.");


       // compare all signatures
        System.out.println("Comparing all signatures...");

        long t_comp_sig = System.nanoTime();

        for (int i = 0; i<numDocs; i++) {
            ArrayList<Integer> signature1 = signatures.get(i);
            for (int j =i+1; j<numDocs; j++){
                ArrayList<Integer> signature2 = signatures.get(j);
                // Count the number of positions in the minhash signature which are equal.
                int count = 0;
                for (int k=0; k<numHashes;k++){
                    if ((int)signature1.get(k)==signature2.get(k)) {
                        count+=1;
                    }
                }
                estJSim[getTriangleIndex(i,j,numDocs)] = (double)count/(double)numHashes;
            }
        }

        long estimatedTime_comp_sig = System.nanoTime() - t_comp_sig;
        double elapsedTimeInSecond_comp_sig = (double) estimatedTime_comp_sig / 1_000_000_000;

        System.out.println("Comparing MinHash signatures took " + Double.toString(
                elapsedTimeInSecond_comp_sig) + " sec.");

        // Diplay Similar Document Pairs
        // true positives
        int tp = 0;
        // false positives
        int fp = 0;

        double threshold = 0.5;

        System.out.println("List of Document Pairs with J(d1,d2) more than " + Double.toString(threshold));
        System.out.println("Values shown are the estimated Jaccard similarity and the actual Jaccard similarity.");
        System.out.println("                  Est.Jaccard Similarity    Actual Jaccard Similarity");

        // Build a dictionary mapping the document IDs to their plagiaries, and
        // vice-versa.
        HashMap<String, String> plagiaries = new HashMap<String, String>();
        try {
            File myObj = new File(truthFile);
            Scanner myReader = new Scanner(myObj);
            while (myReader.hasNextLine()) {
                String line = myReader.nextLine();
                line = line.replace("\n", "");
                String[] docs = line.split(" ");
                plagiaries.put(docs[0], docs[1]);
                plagiaries.put(docs[1], docs[0]);
            }
            myReader.close();
        } catch (FileNotFoundException e) {
            System.out.println("truth file not found.");
        }

        for (int i = 0; i < numDocs; i++) {
            for (int j = i + 1; j < numDocs; j++) {
                // the estimated similarity value for this pair.
                Double estJ = estJSim[getTriangleIndex(i, j, numDocs)];                
                if (estJ > threshold) {
                    // Calculate the actual Jaccard similarity for validation.
                    HashSet<Integer> s1 = docsAsShingleSets.get(docNames.get(i));
                    HashSet<Integer> s2 = docsAsShingleSets.get(docNames.get(j));
                    HashSet<Integer> intersection = new HashSet<Integer>(s1);
                    intersection.retainAll(s2);
                    HashSet<Integer> union = new HashSet<Integer>(s1);
                    union.addAll(s2); 
                    double jacc_sim = (double) intersection.size() / (double) union.size();
                    System.out.println(String.format("%5s --> %5s   %.2f                      %.2f%n", docNames.get(i), docNames.get(j), estJ, jacc_sim));
                    
                    if (plagiaries.get(docNames.get(i)) == null) {
                        continue;
                    }

                    // Check for true positive or false positive.
                    if (plagiaries.get(docNames.get(i)).equals(docNames.get(j))) {
                        tp++;
                    } else {
                        fp++;
                    }
                }
            }
        }
    
    System.out.println("True positives: " + Integer.toString(tp) + " / " + Integer.toString((int)plagiaries.keySet().size() / 2));
    System.out.println("False positives: " + Integer.toString(fp));
    }


    public static void main(String args[]) {
        runMinHash();
    }
}