package com.kanjian.star.search.dao;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.log4j.Logger;
import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Repository;


@Repository
public class StarDAO {

	private static final Logger logger = Logger.getLogger(StarDAO.class);

    @Autowired
    protected SqlSessionTemplate sqlSession;

    public int getTrackMaxId() {
        return (Integer)sqlSession.selectOne("getMaxTrackId");
    }

    public List<HashMap<String, Object>> getTrackList(int minId, int maxId) {
        List<Integer> result = new ArrayList<Integer>();
        Map<String, Object> paras = new HashMap<String, Object>();
        paras.put("start", minId);
        paras.put("end", maxId);
        return sqlSession.selectList("getAllTrack", paras);
    }

    public int getAlbumMaxId() {
        return (Integer)sqlSession.selectOne("getMaxAlbumId");
    }

    public List<HashMap<String, Object>> getAlbumList(int minId, int maxId) {
        List<Integer> result = new ArrayList<Integer>();
        Map<String, Object> paras = new HashMap<String, Object>();
        paras.put("start", minId);
        paras.put("end", maxId);
        return sqlSession.selectList("getAllAlbum", paras);
    }
}
