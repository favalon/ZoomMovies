# ZoomMovies


## 所需计算电影排序的基础信息
### 标签（tag）的分级查询字典（dict）：
- 在我的程序中使用的名称为reverseDict。
由给定标签分级数据生成
上级标签将涵盖下级标签，通过下级标签可以查询到其对应的所有上级标签。

例：
下级标签 boy 的上级标签是 ordinary people， ordinary people 的上级标签是 human。通过下级标签 boy，可以获得它的两个上级标签

### 电影基础信息
这些基础信息都是给定的输入，不由算法产生
这里仅列出计算排序的信息 （Input）
1. ID
2. 年代
3. 评分
4. 标签（标签导入后需要进行处理）
  - 遍历所有标签，将所有的标签的上级标签（直到最上级）加入标签中
  - 根据电影的不同，每个标签都对应一个不同的分数，用于计算排序顺序的分数。\
  每个电影又将标签分为主次标签，比如主要人物是人（因此human为主要标签， 而配角有动物（动物为次要标签）。\
  目前设置主要标签对应分数为3，次要为2，其他（最次级标签）为1（这些对应的分数可能有修改）。
5. 推荐等级
6. 观看年龄段

## 电影排序的计算

### 过滤
根据需求预先过滤电影，接下来只处理过滤后的电影。（比如观看年龄3-5）

### 基础公式
```python
score_new = pirority_weight * self.tags[cluster_name] + release_weight * release_score(self.releaseDate)\
                        + starRating_weight * self.starRating+promotion_weight*self.promotion
```
电影的总体的分计算必须在地图第一层类别开始后才能计算，而不能预先计算

通过调整各项weight的比重来控制分数，控制输出结果。

### 分类
目前设计中，地图一共3层，其中1-2层的分类方式是给定的，第三层是平铺
####第一层的分类
第一层的8大类是给定的（如下），每一类中可以有多个标签 
```python
目前使用的8类
cluster_l1 =[["animal"],
             ["superhero", "star war"],
             ["magic and fantasy characters"],
             ["robots","vehicles","toys","foods","sports",],
             ["ordinary people"],
             ["alien", "space"],["monster", "ghost", "vampire"],
             ["princess", "prince", "queen", "king",	"fairy", "elf", "mermaid", "smurf","snowman"]]
```
通过这些类的标签，将所有电影分别放入8个组中，各组电影允许有重合
通过基础公式对每一组分别计算其中所有电影的分数，并进行排序。
```python
pirority_weight * self.tags[cluster_name]
```
这项评分对于同一个电影在不同类下会给出不同的分数。
- 比如，以superhero为主角（主要标签3分），animal为配角（次要标签2分），robots为其他标签（其他标签1分）。假设pirority=1，这部电影在["superhero", "star war"]类下此项得分为3，、
["animal"]类为2，["robots","vehicles","toys","foods","sports",]类为1.

8类排序（分高->分低）完成后，根据第一层每类显示电影需要的数量提取出排名靠前的电影，如果出现重复则跳过选择下一个。


#### 第二层的分类
目前使用的第二层分类是给定的（如下）
```python
cluster_l2 = ["PG-13 & LA", "PG & LA", "PG-13 & Animation", "PG & Animation"]
```
其中LA为Live action. PG, PG-13是年龄分类（测试中没有使用）
将第一层排序后的8类分别进行第二层分类
根据第二层的分类标签（cluster_l2）将第一层的8组数据再分成对应的4组。
由于电影数量问题导致有些组内电影过少，目前仅使用了"PG & LA" 和 "PG & Animation" 两个标签。\
"PG & LA" 中包括了所有LA的电影（PG和PG-13都在其中），另一个也一样。
假设第二层的4类中每类显示7部电影，那么分别取"PG & LA"和"PG & Animation"组下的前7部电影，放入对应的另外两类。

同样如果这一层电影出现重复跳过选择下一个。

#### 第三层的分类
虽然有通过最次级标签（1分标签）将第二层分组后的每一组电影继续按最次级标签分类排序显示（和第一层做法一样），但实际上由于数量问题，和直接平铺所有电影区别不大
