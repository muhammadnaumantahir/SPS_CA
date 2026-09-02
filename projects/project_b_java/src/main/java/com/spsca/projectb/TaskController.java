package com.spsca.projectb;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
public class TaskController {
  private final Map<Integer, Task> tasks = new ConcurrentHashMap<>();
  private final AtomicInteger sequence = new AtomicInteger(0);

  record TaskRequest(@NotBlank String title) {}
  record Task(int id, String title) {}

  @GetMapping("/health") Map<String,String> health(){ return Map.of("status","ok"); }
  @GetMapping("/tasks") Collection<Task> list(){ return tasks.values(); }
  @PostMapping("/tasks") ResponseEntity<Task> create(@Valid @RequestBody TaskRequest r){ int id=sequence.incrementAndGet(); Task t=new Task(id,r.title()); tasks.put(id,t); return ResponseEntity.status(201).body(t); }
  @GetMapping("/tasks/{id}") ResponseEntity<Task> get(@PathVariable int id){ Task t=tasks.get(id); return t==null?ResponseEntity.notFound().build():ResponseEntity.ok(t); }
  @PutMapping("/tasks/{id}") ResponseEntity<Task> update(@PathVariable int id,@Valid @RequestBody TaskRequest r){ if(!tasks.containsKey(id)) return ResponseEntity.notFound().build(); Task t=new Task(id,r.title()); tasks.put(id,t); return ResponseEntity.ok(t); }
  @DeleteMapping("/tasks/{id}") ResponseEntity<Void> delete(@PathVariable int id){ return tasks.remove(id)==null?ResponseEntity.notFound().build():ResponseEntity.noContent().build(); }
}
