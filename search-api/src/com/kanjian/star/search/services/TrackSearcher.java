package com.kanjian.star.search.services;

import java.io.IOException;
import java.util.List;
import java.util.ArrayList;
import java.nio.file.Paths;

import org.apache.log4j.Logger;

import org.apache.lucene.search.TopDocs;
import org.apache.lucene.search.Sort;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.BooleanQuery;
import org.apache.lucene.search.BooleanClause;
import org.apache.lucene.search.NumericRangeQuery;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.SortField;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.MatchAllDocsQuery;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.store.RAMDirectory;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.document.Document;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.queryparser.classic.QueryParserBase;
import org.apache.lucene.queryparser.classic.ParseException;

import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

@Component
@Service
public class TrackSearcher {

    private static final Logger logger = Logger.getLogger(TrackSearcher.class);

	private static String indexOriginalPath = "/data/star_search/index/original";

    private static IndexReader indexReader = null;
    private static IndexSearcher indexSearcher = null;

	private static final Sort ID_SORT = new Sort(new SortField("id", SortField.Type.INT, true));

    public static int reloadIndex() throws IOException {
        Directory directory = FSDirectory.open(Paths.get(indexOriginalPath+"/track"));
        indexReader = DirectoryReader.open(directory);
        indexSearcher = new IndexSearcher(indexReader);
        TopDocs results = indexSearcher.search(new MatchAllDocsQuery(), 100);
        logger.info(""+results.totalHits);
        return 0;
    }

    public static int searchTrack(String key, int start, int rows, List<Integer> result) throws IOException, ParseException {
        return 0;
        if (indexSearcher == null) {
            reloadIndex();
        }
        result = new ArrayList<Integer>();
        Query query = buildQuery(key);
        logger.info(query);
        Sort sort = ID_SORT;
        if (query != null) {
            TopDocs topDocs = indexSearcher.search(query, 3000000, sort);
            ScoreDoc[] hits = topDocs.scoreDocs;
            for (int i = start;i < Math.min(topDocs.totalHits, (start+rows));i++) {
                Document doc = indexSearcher.doc(hits[i].doc);
                result.add(Integer.parseInt(doc.get("id")));
            }
            logger.info("nummber of hits: " + topDocs.totalHits);
            return topDocs.totalHits;
        }
        return 0;
    }

    private static Query buildQuery(String query, int durationStart, int durationEnd) throws ParseException {
        BooleanQuery bq = new BooleanQuery();
        Analyzer analyzer = new StandardAnalyzer();
        QueryParser titleParser = new QueryParser("title", analyzer);
        titleParser.setDefaultOperator(QueryParser.Operator.AND);
        Query titleQuery = null;
        if (query == null) {
            titleQuery = titleParser.parse("kanjiansdxqfx");
        } else {
            titleQuery = titleParser.parse(QueryParserBase.escape(query + " kanjiansdxqfx"));
        }
        bq.add(titleQuery, BooleanClause.Occur.MUST);

        if (durationStart <= durationEnd) {
            NumericRangeQuery<Integer> durationQuery = NumericRangeQuery.newIntRange("duration", durationStart, durationEnd, true, true);
            bq.add(durationQuery, BooleanClause.Occur.MUST);
        }

        return bq;
    }
    private static Query buildQuery(String query) throws ParseException {
        return buildQuery(query, 0, 999);
    }
}
