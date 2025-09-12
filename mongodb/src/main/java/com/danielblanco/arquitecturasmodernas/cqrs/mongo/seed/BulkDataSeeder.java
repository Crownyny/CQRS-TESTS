package com.danielblanco.arquitecturasmodernas.cqrs.mongo.seed;

import com.danielblanco.arquitecturasmodernas.cqrs.mongo.model.Comment;
import com.danielblanco.arquitecturasmodernas.cqrs.mongo.model.Post;
import com.danielblanco.arquitecturasmodernas.cqrs.mongo.model.Reaction;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.stereotype.Component;

@Component
public class BulkDataSeeder implements ApplicationRunner {

  private static final Logger log = LoggerFactory.getLogger(BulkDataSeeder.class);

  private final MongoTemplate mongoTemplate;

  public BulkDataSeeder(MongoTemplate mongoTemplate) {
    this.mongoTemplate = mongoTemplate;
  }

  @Value("${data.seed.enabled:true}")
  private boolean seedEnabled;

  @Value("${data.seed.posts:1000000}") // 1 millón de posts
  private int posts;

  @Value("${data.seed.comments.min:0}")
  private int minCommentsPerPost;

  @Value("${data.seed.comments.max:5}")
  private int maxCommentsPerPost;

  @Value("${data.seed.reactions.min:0}")
  private int minReactionsPerComment;

  @Value("${data.seed.reactions.max:3}")
  private int maxReactionsPerComment;

  @Value("${data.seed.batchSize:5000}")
  private int batchSize;

  private static final String[] EMOJIS = new String[]{
      "👍", "❤️", "😂", "🎉", "🚀", "😮", "😢", "👎"
  };

  @Override
  public void run(ApplicationArguments args) {
    if (!seedEnabled) return;

    long existing = mongoTemplate.getCollection("posts").estimatedDocumentCount();
    if (existing > 0) {
      log.info("Posts already exist ({}), skipping seed.", existing);
      return;
    }

    List<Post> buffer = new ArrayList<>(batchSize);
    ThreadLocalRandom rnd = ThreadLocalRandom.current();

    log.info("Starting seed of {} posts...", posts);
    long startTime = System.currentTimeMillis();

    for (int i = 1; i <= posts; i++) {
      Post p = new Post();
      p.setId(UUID.randomUUID().toString());
      p.setContent("Post " + i);

      // Genera comentarios
      int commentsCount = randomBetween(rnd, minCommentsPerPost, maxCommentsPerPost);
      if (commentsCount > 0) {
        List<Comment> comments = new ArrayList<>(commentsCount);
        for (int c = 1; c <= commentsCount; c++) {
          Comment comment = new Comment();
          comment.setId(UUID.randomUUID().toString());
          comment.setContent("Comment " + p.getId() + "-" + c);

          int reactionsCount = randomBetween(rnd, minReactionsPerComment, maxReactionsPerComment);
          if (reactionsCount > 0) {
            List<Reaction> reactions = new ArrayList<>(reactionsCount);
            for (int r = 0; r < reactionsCount; r++) {
              Reaction reaction = new Reaction();
              reaction.setId(UUID.randomUUID().toString());
              reaction.setEmoji(EMOJIS[rnd.nextInt(EMOJIS.length)]);
              reactions.add(reaction);
            }
            comment.setReactions(reactions);
          }
          comments.add(comment);
        }
        p.setComments(comments);
      }

      buffer.add(p);

      // Insertar batch
      if (buffer.size() >= batchSize) {
        mongoTemplate.insert(buffer, Post.class);
        buffer.clear();
        log.info("Inserted {} posts so far...", i);
      }

      // Ceder al GC cada 100k posts
      if ((i % 100_000) == 0) {
        try { Thread.sleep(50); } catch (InterruptedException ignored) {}
      }
    }

    // Insertar resto de buffer
    if (!buffer.isEmpty()) {
      mongoTemplate.insert(buffer, Post.class);
      buffer.clear();
    }

    long endTime = System.currentTimeMillis();
    log.info("Seed completed: {} posts in {} ms", posts, (endTime - startTime));
  }

  private int randomBetween(ThreadLocalRandom rnd, int min, int max) {
    if (max <= min) return Math.max(min, 0);
    return rnd.nextInt((max - min) + 1) + min;
  }
}
