package com.spsca.projectb;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class TaskApiTest {
    @Autowired MockMvc mvc;

    @Test void healthAndCrudContract() throws Exception {
        mvc.perform(get("/health")).andExpect(status().isOk()).andExpect(jsonPath("$.status").value("ok"));
        mvc.perform(post("/tasks").contentType(MediaType.APPLICATION_JSON).content("{\"title\":\"write tests\"}"))
            .andExpect(status().isCreated()).andExpect(jsonPath("$.id").value(1));
        mvc.perform(get("/tasks/1")).andExpect(status().isOk()).andExpect(jsonPath("$.title").value("write tests"));
        mvc.perform(put("/tasks/1").contentType(MediaType.APPLICATION_JSON).content("{\"title\":\"better tests\"}"))
            .andExpect(status().isOk()).andExpect(jsonPath("$.title").value("better tests"));
        mvc.perform(delete("/tasks/1")).andExpect(status().isNoContent());
        mvc.perform(get("/tasks/1")).andExpect(status().isNotFound());
    }

    @Test void multipleIdsAreDistinct() throws Exception {
        mvc.perform(post("/tasks").contentType(MediaType.APPLICATION_JSON).content("{\"title\":\"first\"}"));
        mvc.perform(post("/tasks").contentType(MediaType.APPLICATION_JSON).content("{\"title\":\"second\"}"));
        mvc.perform(get("/tasks/2")).andExpect(status().isOk()).andExpect(jsonPath("$.id").value(2));
    }

    @Test void emptyTitleRejected() throws Exception {
        mvc.perform(post("/tasks").contentType(MediaType.APPLICATION_JSON).content("{\"title\":\"\"}"))
            .andExpect(status().isBadRequest());
    }
}
